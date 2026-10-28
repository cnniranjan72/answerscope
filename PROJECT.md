# Project specification

Requirement IDs refer to [PROBLEM_STATEMENT.md](PROBLEM_STATEMENT.md). Status: **M** mandatory and done, **O** optional and done, **D** deferred, **X** intentionally omitted.

## Inputs (verified by inspection, 28 Oct 2026)
* 50 prompts. `…:001`–`025` name Kasparro (branded); `026`–`050` do not (unbranded discovery).
* 150 responses, 50 per engine, all `captured`. `model_version`: aimode always null, chatgpt `gpt-5-5` (45) / null (5), gemini `3.5 Flash-Lite`. `force_web_search`: true for 50, null (unknown) for 100.
* `answer_text` = answer + appended `\n\nCitations:\n[n] url` list (149/150). `answer_markdown` is another view of the same answer and is not analysed separately.
* 2,439 citation occurrences in 149 responses; 1,659 distinct (response, URL) pairs; publication dates all null; 677 titles null.
* The pack checker passes (`py -3 assignment/tools/check_pack.py`).

## Decisions (summary; reasons in [claude-code/DECISION.md](claude-code/DECISION.md))

**Classification (R2, R3).** Labels: `mentioned` (absent = not mentioned), `recommended`, `negative`, plus `entity_confusion` (Kasparro confused with Kaspr or misidentified), because inspection showed it is a major pattern. Competitors are named vendors in the AI visibility/SEO space; engines and review sites are excluded. Position is recorded only from explicit ranked lists.

**Citation policy citation-v1 (R3).** Occurrences = rows. Distinct = normalised URL per response: lower-case host, no `www.`, no fragment, no tracking parameters, no trailing slash. First-party = `kasparro.com`. Other Kasparro-related URLs (LinkedIn, job boards) are counted separately. Support is always `unverified`.

**Prompt categories cat-v1 (R20).** Branded vs unbranded (does the question name Kasparro?) × topic from ordered keyword rules: comparison, pricing_terms, onboarding_access, trust_efficacy, capability_fit.

**Score vis-v1 (R4).** 0–100 = clamp(40·mentioned + 40·recommended + 20·first-party cited − 30·negative − 20·entity confusion).
* Failed or skipped answers have no score and are excluded from rate denominators. Coverage reports them.
* Rates carry 95% Wilson intervals.
* Branded and unbranded are always reported separately; mixing them would blur two different questions ("do engines know Kasparro?" vs "do engines bring Kasparro up?").

**Diagnostics report-v1 (R21).** Four candidate patterns are computed from stored results:
* unbranded discovery gap;
* entity confusion;
* credibility gap (negatives in branded answers);
* branded recommendation win.

They are ranked by affected responses × severity weight. The top 3 become D1–D3, each with a templated remedy. All quotes are verified evidence spans. Analysts edit, and reviewers approve.

## API (R5, R6, R10)

| Method | Path | Role | Notes |
|---|---|---|---|
| GET | `/health` | none | DB check, versions |
| GET | `/whoami` | any | server-derived identity |
| POST | `/datasets` | analyst | records in body; per-record outcomes; 201 |
| POST | `/datasets/pack` | analyst | server-configured pack |
| GET | `/datasets/{id}` | any | ledger + rejections |
| POST/GET | `/analyses`, `/analyses/{id}` | analyst / any | synchronous; counts + scorecard |
| GET | `/analyses/{id}/results`, `…/results/{rid}/trace` | any | per-response results; model call attempts |
| POST/GET | `/reports`, `/reports/{id}`, `/reports/{id}/versions/{n}` | analyst / any | draft from analysis; history |
| PATCH | `/reports/{id}` | analyst | `base_version` required |
| POST | `/reports/{id}/submit` | analyst | evidence checks; freezes |
| POST | `/reports/{id}/decision` | reviewer | `version`, `decision`, `comment`, `content_sha256` |
| GET | `/reports/{id}/export[?version=n]` | any | approved content only |

Errors: 401 unauthenticated, 403 wrong role, 404 unknown id, 409 stale/invalid transition/not approved/hash mismatch/integrity, 422 validation or evidence check, 500 generic.

## Requirement → implementation → verification

| ID | Status | Implementation | Verified by |
|---|---|---|---|
| R1 | M | `response_results` one row per response; `succeeded/failed/skipped` + reason | `test_failed_analysis_is_not_a_zero_score`, `test_skipped_when_body_too_large`, live run counts |
| R2–R3 | M | `analyzer.py`, `prompts/classify_v1.md`, `citations.py` | eval per-label metrics; `test_citation_policy` |
| R4 | M | `scoring.py` | `test_score_*`, eval arithmetic check |
| R5–R6 | M | `app/api/routes.py`, `/docs`, README examples | API tests, HTTP smoke run |
| R7 | M | bounded attempts/timeouts/output tokens/input size; output contract + grounding | `test_failures_are_explicit_and_bounded`, `test_extra_fields_rejected` |
| R8 | M | `model_calls`, `analysis_runs`, execution mode everywhere, `.env.example` | trace endpoint test |
| R9 | M | delimiters, deterministic permissions, per-record transactions | S02 eval case, `test_untrusted_text_is_delimited_as_data` |
| R10–R11 | M | structured errors; idempotent import | ingestion tests |
| R12–R14 | M | `security.py`, `review.py`, triggers | `tests/test_review.py` |
| R15–R19 | M | `evaluation/` | `python -m evaluation.run_eval` |
| R20–R21 | M | `scoring.aggregate`, `reporting.py` | eval diagnostics check |
| R22 | M | `tests/` | pytest |
| R23–R24 | M | docs, outputs, replay | final audit in HANDOFF |
| Console UI | O | `app/static/index.html` | HTTP smoke + JS syntax check (manual visual check pending) |
| Job queue / resume, review expiry, concurrency beyond hash+latest checks | D | described in ARCHITECTURE/SECURITY | n/a |
| Opening cited pages to verify claim support; hosted LLM adapter; Docker; vector search | X | out of scope or unpaid/unapproved | n/a |

## Definition of done
Pack checker passes; `pytest` green; evaluation command writes a report; every response has an outcome in the submitted analysis; one report version approved and exported, with denial paths demonstrated; README commands work from a clean clone; no secrets committed; decision note and time log are truthful.
