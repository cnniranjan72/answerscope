# Handoff (final, 29 Oct 2026)

## State
Complete. Every deliverable in the brief exists and was produced by the commands below. The only step left is the candidate sending the submission.

| Deliverable | Path | Produced by |
|---|---|---|
| Analysis output (scores, coverage, 3 diagnostics, 3 remedies, active time) | `outputs/analysis_output.json` | `python -m app.cli write-output 26bd51fb-8804-45ef-8a1f-df4e46f7b3fa --active-minutes 170` |
| Approved report export (v1 of `7d80ca70`, approved by the candidate as reviewer) | `outputs/approved_report_export.json` | `review.export`; identical content, approval and hash to the candidate's console download in `outputs/console_check/` |
| Evaluation report | `evaluation/results/eval_report.md`, `eval_results.json` | `python -m evaluation.run_eval` (replay, labels-v3) |
| Decision note | `DECISION_NOTE.md` | – |
| Labels and decision log | `evaluation/cases/labels_v3.jsonl`, `candidate_review_log.jsonl` | `python -m evaluation.candidate_review` |
| Model recordings | `replay/classify_v1/` (150 answers + S01, S02) | `python -m app.cli analyse --provider ollama --record [--only-unrecorded]`; `run_eval --provider ollama --record --record-only S01,S02` |

## Verified (commands run, output observed, 29 Oct)
* `python -m pytest -q`: **86 passed**.
* Live run: 150/150 recorded. It was stopped for low memory at 91/150 and resumed with `--only-unrecorded`, with no duplicates (the resume skips answers that already have a recording). 171 calls, 147 ok and 24 invalid; mean 63 s per call.
* Replay analysis on the main DB: 150 eligible, 148 succeeded, 2 failed (non-verbatim quotes), 0 skipped.
* Evaluation: the final split has 14 cases, and every case for both systems succeeded. Diagnostics checker: 0 problems on the generated report; 4/4 injected defects detected; 19/19 score arithmetic checks.
* Console: the evidence-removal control was checked in headless Chrome on a copy of the DB (port 8766). The candidate then used it on the real report, submitted, approved and exported.
* Export hash: recomputed from the export file after removing the export-only evidence fields, and it matches (`test_export_hash_is_verifiable_from_the_file`).
* Secret scan: neither token value appears in any commit; no `.env`, pack, DB or zip files are tracked.
* Clean clone: see the final entry below.

## Known issues (all disclosed in EVALUATION.md / DECISION_NOTE.md)
* The model over-predicts `recommended` (final-split precision 0.29). It was not retuned on the holdout. The report states that 40/73 is likely an overestimate.
* Product misattribution (H06 class) is not covered by the prompt, so entity confusion (8/73) is a lower bound.
* There is one model run, so variance is not measured. Citation support is not verified.
* A confused mention scores 20 > absent 0 under vis-v1 (the candidate's decision: keep it and disclose it).
* Live analysis via HTTP is synchronous and impractical for 150 answers on this GPU, so the CLI is used instead.

## Clean-clone check (29 Oct, commit 4b6a699)
Fresh clone, then: venv, `pip install -r requirements.txt`, new random tokens in `.env`, pack checker (valid), init-db, then:
* pytest: **86 passed**;
* import and **replay analysis**: 150 eligible, 148 succeeded, 2 failed;
* `run_eval`: the report is **identical to the committed one** apart from the timestamp;
* workflow demo: **21/21 steps**.

Total **79 s**. The published metrics regenerate from the committed recordings and labels.

## Submission archive
`git archive --format=zip -o ../answerscope_submission.zip HEAD` creates a local file only. It contains tracked files only: no `.env`, no `assignment/` pack, no DB, no `INTERVIEW_PREP.md`. Not sent anywhere; the candidate sends it.
