# Console check artefacts (not the submission report)

`report-2daa8866-v1.json` was exported by the candidate from the review console (http://localhost:8000/) on 28 Oct 2026 after a manual walkthrough:
1. Analyst: import, analysis (**stub** provider), create report, edit, submit.
2. Reviewer: approve with a comment, export.

It demonstrates that only an approved, hash-identified version exports, with reviewer, comment, timestamp and exact evidence offsets. Its labels come from the **stub** (deterministic baseline), so it is **not** evidence of model quality and is not the submitted analysis. The submitted report is produced from the replayed local-model analysis.
