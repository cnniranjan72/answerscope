# Console check artefacts (not the submission report)

`report-2daa8866-v1.json` was exported by the candidate from the review console (http://localhost:8000/) on 28 Oct 2026 after a manual walkthrough:
1. Analyst: import, analysis (**stub** provider), create report, edit, submit.
2. Reviewer: approve with a comment, export.

It demonstrates that only an approved, hash-identified version exports, with reviewer, comment, timestamp and exact evidence offsets. Its labels come from the **stub** (deterministic baseline), so it is **not** evidence of model quality and is not the submitted analysis. The submitted report is produced from the replayed local-model analysis.

`report-7d80ca70-v1_console_export.json` is the candidate's own console download of the **submission** report (approved 29 Oct 2026). `outputs/approved_report_export.json` is the same approved version re-exported by the service. It has the same content, approval and hash, and adds the `content_sha256_covers` note that explains how to verify the hash.
