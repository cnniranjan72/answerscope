# Handoff (updated 28 Oct 2026, 23:20 IST)

## Verified (commands run, output observed)
* Pack checker: valid (from repo root and inside a clean clone).
* `python -m pytest -q`: **73 passed** (main repo and a clean clone).
* Clean clone → venv → install → `.env` → init-db → pytest → stub eval → workflow demo: **96 s** end to end.
* `scripts/demo_review_workflow.py`: 21/21 steps returned the expected status (403 wrong role, 409 rejected/unapproved/stale export, 409 hash mismatch, explicit old-version export marked superseded).
* HTTP smoke test via uvicorn: `/health`, `/`, `/docs`, import, analysis, report, 403 and 409 paths.
* Label audit: `python -m evaluation.audit_labels` OK (all spans exact, scores match vis-v1).
* Secret scan: token values in no commit; `.env`, `assignment/`, `var/` untracked.

## In progress
* Live local-model run with recording (`var/live_run.log`): 22/150 at 23:16, about 75 s per call, ETA ≈ 02:30–03:00. If interrupted: `DATABASE_PATH=var/live.db python -m app.cli analyse --provider ollama --record --only-unrecorded`.

## Done since last update (28 Oct, ~23:45)
* H06 adjudicated after candidate manual check MC-01 → entity_confusion = true; labels frozen as `labels_v2.jsonl` (now the eval default).
* F5 matcher fix (second-pass list-marker hiding) + regression test; H11 reported with and without (`final_sensitivity`).
* Console verified: headless Chrome (Playwright) analyst/reviewer flows, plus the candidate's manual walkthrough on :8000. The export is filed in `outputs/console_check/` (stub; not the submission report).
* 77 tests pass.

## Waiting on the candidate
1. Personally review and approve or reject the final (replay-based) report in the console as the reviewer.
2. Add own active time to TIME_LOG.md.

* Mobile layout fixed: page width 390 px at a 390 px viewport (verified in headless Chrome).
* Analysis runs now report call statistics (calls, outcomes, total/mean seconds, cost).

## Remaining (after the run and the freeze)
1. Final analysis: `python -m app.cli analyse --provider replay` (main DB), then `python -m app.cli write-output <id>`.
2. `python -m evaluation.run_eval --labels evaluation/cases/labels_v2.jsonl`; fill EVALUATION.md results.
3. Review diagnostic wording against real numbers; create the report; candidate approves; save the export to `outputs/approved_report_export.json`.
4. DECISION_NOTE.md (one page), final TIME_LOG, final quality-gate pass, private archive.

## Known issues
* Live analysis via HTTP is synchronous and impractical for 150 answers on this GPU (CLI is used instead; documented).
* A confused mention scores 20 > absent 0 under vis-v1 (candidate decision: keep, note as limitation).
* The prompt does not cover product misattribution (H06 class); not changed, to avoid tuning on holdout.
