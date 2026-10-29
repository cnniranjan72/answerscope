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

## Prompt versions, evidence policy and review deadline (29 Oct sprint)

* **Prompt registry** (`analyzer.PROMPTS`). `classify-v2` is the default since 29 Oct 2026 (promotion record in DECISION_NOTE.md). `classify-v1` stays registered: the approved run, its recordings and the evaluation of record (`run_eval` and the keyword baseline are pinned to its contract). Select a version with `--prompt-version`. Each version has its own prompt file, output contract and replay directory (`replay/classify_v1/`, `replay/classify_v2/`). The input hash includes the version, so a recording can never be replayed under the other prompt. classify-v2 adds an explicit `recommendation_type` decision and three deterministic rules:
  1. recommended must agree with the type;
  2. recommendation evidence must sit in a sentence that names Kasparro;
  3. a confused entity cannot be recommended.
* **Recordings** are written atomically (temp file + rename). Resume (`--only-unrecorded`, `compare --fill-v1/--fill-v2`) treats a missing, truncated or input-hash-mismatched recording as unrecorded.
* **evidence-v2** (`reporting.evidence_warnings`) adds advisory flags per evidence item: very short quote, response lacks the claimed label, quote not in a sentence that names Kasparro, answer also confuses the entity. They are returned beside the report (`evidence_warnings`), shown in the console, and included in the export outside the hashed content. Drafts prefer quotes without warnings. **evidence-v3** (report generator `report-v3`) applies the same preference to the unbranded diagnostic's competitor quotes and flags assistant follow-up offers ("Would you like…"). Warnings never block; a human decides.
* **claims-v1** (`app/services/claims.py`): reviewer advisory for possible product misattribution: a paragraph that names Kasparro and states a price, cited only to non-Kasparro domains. Returned beside the report and in the export (`claim_advisories`), outside the hashed content; never counted in a diagnostic.
* **Report comparison** (`app/services/report_diff.py`; `GET /reports/{id}/compare?against=`, `python -m app.cli report-diff`, and a console card): compares the latest approved version of each report (else the latest), separates method changes (prompt, score, categories, report generator, model, mode) from data changes, and marks each rate change by whether the two 95% Wilson intervals overlap. It is descriptive: with a method change, differences are attributed to the method, not the engines.
* **Review deadline.** Submit sets `review_due_at` (`REVIEW_DUE_HOURS`, default 72). An overdue version stays `submitted`, is flagged `review_overdue`, is never approved or rejected by timeout, and export keeps refusing. Databases from before this change are migrated additively by `init_db`.

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
* **Single process, SQLite.** `BEGIN IMMEDIATE` serialises writers, which is enough for two local users. What exists today: a decision must name the latest version and its content SHA-256, Decisions run inside `BEGIN IMMEDIATE`, so a second concurrent decision sees the version is no longer `submitted` and gets 409. `UNIQUE(report_id, version)` on decisions is the database backstop. An edit must name its `base_version`, so a stale edit gets 409.
* **Review expiry (implemented 29 Oct as a deadline flag; escalation routing remains future work).** Submit stores `review_due_at` (`REVIEW_DUE_HOURS`, default 72). A version past its deadline stays `submitted` and is flagged `review_overdue` (API and console banner). It is **never** approved by timeout. Not implemented: routing an overdue review to a named second reviewer. A decision on an overdue version still requires the hash match. Export keeps refusing until a human approves.
* **Concurrency at scale (future work).** With several reviewers or processes: Postgres with row locks (`SELECT … FOR UPDATE`) on the version, a review claim with a lease so two reviewers do not work on the same version, and optional two-reviewer quorum for client exports. Analysis would move to a job queue with per-response checkpoints. The CLI `--only-unrecorded` resume is the current stand-in.
* **Recommendation position** is recorded but not scored, because it is rarely observable for Kasparro in this snapshot.
