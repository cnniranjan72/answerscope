# Architecture

One FastAPI process, one SQLite file, synchronous bounded processing. Each module has one job. The API layer stays thin; the logic lives in `app/services/`.

```
HTTP (FastAPI, bearer token -> server-configured identity)
  │
  ├─ /datasets ─────────► ingestion.py   validate each record (Pydantic), idempotent insert, ledger
  ├─ /analyses ─────────► analysis.py    per-response loop, one transaction per result
  │                         ├─ text.py        strip appended citation list, locate quotes → offsets
  │                         ├─ analyzer.py    prompt → provider → validate/ground → bounded retry
  │                         │    └─ llm.py    OllamaProvider | ReplayProvider | StubProvider
  │                         ├─ citations.py   citation-v1 counting/dedup, first-party detection
  │                         ├─ categories.py  cat-v1 branded/unbranded + topic rules
  │                         └─ scoring.py     vis-v1 components, score, aggregates, Wilson CI
  ├─ /reports ──────────► reporting.py   ranked diagnostics + remedies from stored results, evidence checks
  └─ /reports/{id}/... ─► review.py      versions, submit, decision, export (BEGIN IMMEDIATE)
SQLite (app/db/schema.sql) + immutability triggers
```

## Data model

| Table | Purpose |
|---|---|
| `datasets`, `dataset_records` | Every import and the outcome of every submitted record (inserted / reused / rejected + reason). |
| `prompts`, `responses`, `citations` | Supplied records with their **original IDs**, typed columns, `raw_json` verbatim and a canonical SHA-256. Unknown values stay NULL. |
| `analysis_runs` | Provider, execution mode, model, prompt/score/category versions, bounds, counts. |
| `response_results` | Exactly one row per (analysis, response): `succeeded`, `failed` or `skipped`, with reason, labels + evidence spans, citation features, score components and score (NULL unless succeeded). |
| `model_calls` | Every attempt: mode, model, prompt version, input SHA-256, outcome, error, latency, bounded raw output. |
| `reports`, `report_versions` | Append-only versions with status, canonical content JSON and its SHA-256. |
| `review_decisions` | Immutable: version, decision, comment, reviewer, role, content hash, time. |

## Analysis flow per response

1. `answer_body()` removes the appended `Citations:` URL list. Citations come from `citations.jsonl` instead, so a URL is a citation, never a "mention".
2. Skip with reason if the body is empty or longer than `MAX_INPUT_CHARS`. Long bodies are not truncated, because that could drop the evidence.
3. Build messages: versioned system prompt plus question and answer inside explicit untrusted-data delimiters. The input SHA-256 identifies the exact model input.
4. Call the provider (timeout bounded). Validate the output in this order:
   1. It must be JSON.
   2. It must match the Pydantic contract; extra fields are forbidden.
   3. Every label quote must be found in the body. The stored quote is the exact source span with its offsets.
   4. "Mentioned" must agree with the lexical presence of the name.
   5. A recommendation implies a mention.
   6. A position requires a ranked list.
   7. Competitor names must appear in the text; review sites and engines are filtered out by policy.
5. A rejected output is retried with the validator's messages, up to `MODEL_MAX_ATTEMPTS` (3). Timeouts and provider errors are retried too. After the last attempt the response is recorded as **failed** with its reason; a failure never becomes a zero.
6. Score from components; persist the result and all attempts in one transaction. One record failing never affects others.

## Review state machine

```
draft ──submit(version)──► submitted ──decision(version, sha, comment)──► approved | rejected
  ▲  edit in place                │ edit                                     │ edit
  └───────────────────────────────┴──────── new draft (version + 1) ◄────────┘
```

* Only the latest version can be edited, submitted or decided (`409 stale_version` otherwise). PATCH must name `base_version`, which prevents lost updates.
* Submit re-runs evidence checks and refuses with `422` if any quote is not in its response, a remedy does not follow from its diagnostic, or there are not exactly 3 + 3 items.
* A decision must quote the content SHA-256 the reviewer read. A mismatch gives `409 content_mismatch`.
* Export without `?version` targets the latest version and refuses unless it is approved. An older approved version is exportable only by explicit number and is labelled `superseded_by_version`. Export also recomputes the content hash and compares it with the stored hash and the decision's hash.
* SQLite triggers reject content updates on non-draft versions, invalid status transitions, deletion of versions, and any change to decisions.

## Limits (deliberate)

* **Synchronous analysis.** A replay run of 150 answers takes seconds. A live local-model run takes hours, so it is run from the CLI (`python -m app.cli analyse --provider ollama --record`) rather than holding an HTTP request open. A job queue with resumable runs is the next step.
* **Single process, SQLite.** `BEGIN IMMEDIATE` serialises writers, which is enough for two local users. Simultaneous-review protection beyond the hash and latest-version checks, review expiry, and multi-reviewer policies are future work.
* **Recommendation position** is recorded but not scored, because it is rarely observable for Kasparro in this snapshot.
