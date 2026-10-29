# Handoff (updated 29 Oct 2026, 07:20 IST)

## Verified (commands run, output observed)
* Clean clone of `22815dd`+ → venv → install → `.env` → pack checker (valid) → init-db → pytest (**82 passed**) → stub eval → workflow demo (**21/21 steps**): **93 s** end to end (29 Oct, 07:15).
* `scripts/demo_review_workflow.py`: 403 wrong role, 409 rejected/unapproved/stale export, 409 hash mismatch, explicit old-version export marked superseded.
* HTTP smoke test via uvicorn, and headless-Chrome analyst/reviewer flows (28 Oct). The candidate's manual console walkthrough on :8000 was filed in `outputs/console_check/` (stub; not the submission report).
* Secret scan (29 Oct): neither token value appears in any commit; `.env`, `assignment/`, `var/` and `INTERVIEW_PREP.md` are untracked.

## Labels
* labels-v1 (draft) → labels-v2 (frozen 28 Oct after adjudication of disputed cases) → **labels-v3** (29 Oct). For v3 the candidate decided all 19 cases one at a time (`evaluation/cases/candidate_review_log.jsonl`), using an AI-assisted second-opinion audit as input. There are 2 changes: T01 negative marked ambiguous, and H03's evidence span extended. S02 is recorded as a deliberate exception. v2 is pinned by hash in a test. `run_eval` defaults to v3. See LABEL_AUDIT.md §10.

## In progress
* Live local-model run with recording. It was stopped for low memory at 91/150 (≈00:30) and resumed at 06:30 with `--only-unrecorded`. Log: `var/live_resume.log`.

## Remaining (after the run)
1. Final analysis: `python -m app.cli analyse --provider replay` (main DB), then `python -m app.cli write-output <id> --active-minutes <candidate total>`.
2. `python -m evaluation.run_eval`; fill in the EVALUATION.md results and the `⟦…⟧` placeholders in DECISION_NOTE.md.
3. Check the diagnostic wording against the real numbers; create the report. **The candidate reviews and approves it in the console.** Save the export to `outputs/approved_report_export.json`.
4. TIME_LOG §5 (approval time), final quality-gate pass, private archive (`git archive --format=zip -o ../answerscope_submission.zip HEAD`; supplied data is excluded because it is untracked).

## Known issues
* Live analysis via HTTP is synchronous and impractical for 150 answers on this GPU, so the CLI is used instead (documented).
* A confused mention scores 20 > absent 0 under vis-v1. Candidate decision: keep, and note it as a limitation.
* The prompt does not cover product misattribution (the H06 class). Not changed, to avoid tuning on the holdout.
