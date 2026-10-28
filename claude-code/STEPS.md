# Implementation steps (six phases)

Each phase lists its objective, dependencies, files, tasks, acceptance criteria, commands and artifacts. Status reflects what was actually done.

## 1. Source inspection, integrity verification, requirements mapping (done)
* **Depends on:** extracted pack at `assignment/`.
* **Tasks:** read the PDF, brief, READ_ME, schema and fixtures; run the checker; profile counts, schemas, engines, citations; record evidence-relevant facts.
* **Accept:** the checker passes; counts 50/150/2,439 confirmed; requirement list R1–R24.
* **Command:** `py -3 assignment/tools/check_pack.py`
* **Artifacts:** PROBLEM_STATEMENT.md, PROJECT.md inputs section.

## 2. Minimal backend, validated ingestion, persistence (done)
* **Depends on:** 1.
* **Files:** `app/config.py`, `app/db/*`, `app/schemas.py`, `app/services/ingestion.py`, `app/api/routes.py`, `app/main.py`.
* **Tasks:** schema with raw JSON + hashes; per-record validation; idempotent import ledger; health; structured errors; bearer identities.
* **Accept:** import 50/150/2,439; re-import is all `reused`; conflicting content is rejected; invalid records are rejected with reasons while valid ones are kept.
* **Tests:** `tests/test_ingestion.py`, `tests/test_config.py`.

## 3. Classification, scoring, model adapter, traceability (done)
* **Depends on:** 2.
* **Files:** `prompts/classify_v1.md`, `app/services/{text,llm,analyzer,baseline,citations,categories,scoring,analysis}.py`, `app/cli.py`.
* **Tasks:** Ollama/replay/stub providers; output contract; grounding; bounded retries with feedback; per-response outcomes; call traces; vis-v1 score; aggregates by engine × segment × topic; paired prompts.
* **Accept:** every response has an outcome; failures are explicit; replay refuses stale recordings.
* **Tests:** `tests/test_analyzer.py`, `tests/test_scoring.py`.
* **Command:** `python -m app.cli analyse --provider ollama --record`

## 4. Reports, versioning, review authorisation, controlled export (done)
* **Depends on:** 3.
* **Files:** `app/services/{reporting,review}.py`, `app/security.py`, triggers in `schema.sql`, `app/static/index.html`.
* **Tasks:** ranked diagnostics/remedies with verified evidence; PATCH with base_version; submit with evidence checks; hash-bound decisions; export rules; console.
* **Accept:** wrong role 403; rejected never exports; edit-after-approval creates v+1 and blocks export of latest; v1 still exportable explicitly and marked superseded.
* **Tests:** `tests/test_review.py`.

## 5. Evaluation, baseline, failure/fix, regression (done; final numbers in EVALUATION.md)
* **Depends on:** 3, 4, and the recorded live run.
* **Files:** `evaluation/build_cases.py`, `evaluation/cases/labels_v1.jsonl`, `evaluation/run_eval.py`, `evaluation/FAILURES.md`.
* **Accept:** the tuning/final split is reported separately; baseline and model run on the same cases; arithmetic check has 0 mismatches; the negative evidence case is fully detected; F1–F4 have regression tests.
* **Command:** `python -m evaluation.run_eval`

## 6. Documentation, reproducibility, final audit, submission (see HANDOFF.md)
* **Tasks:** README commands verified from a clean clone; analysis output and approved export written; decision note; time log; secret scan; private archive.
* **Accept:** QUALITY_GATES.md all ticked with observed results.
