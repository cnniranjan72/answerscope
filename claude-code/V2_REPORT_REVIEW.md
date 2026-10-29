# classify-v2 report draft: AI-prepared review notes

**Status:** report `6edb78b8-2db6-4633-b9c7-f1a6aa8b8e4f`, version 1, **draft**, created 29 Oct 2026 from analysis `f144fd60` (classify-v2, replay, 149/150 succeeded) with report generator `report-v3` (evidence-v3). It supersedes draft `1dcbae40` (report-v2), which stays in the database unedited and unsubmitted: **ignore it** (same analysis, same metrics and scorecard; its D1/R1 had four weak quotes that evidence-v3 now avoids). Nothing has been edited, submitted or approved. The notes below were prepared by the AI assistant. The edits, the submission and the approve or reject decision belong to the candidate (analyst, then reviewer). The approved v1 report `7d80ca70` is unchanged.

## What changed against the approved report (same 31 Jul 2026 capture)

| | approved `7d80ca70` (classify-v1) | this draft (classify-v2) |
|---|---|---|
| succeeded / failed | 148 / 2 | 149 / 1 |
| recommended | 40/148 | 12/149 |
| negative (branded) | 30/73 | 23/74 |
| entity confusion (branded) | 8/73 | 9/74 |
| D3 | "some engines present it as a fit" | "Engines confuse Kasparro with other entities (notably Kaspr)" |

The differences come from the method change, not from new engine answers. On holdout2, v2 cut recommended false positives from 10 to 2 (EVALUATION.md).

## Suggested analyst edits (console, signed in as analyst)

**Remove these evidence quotes** (tick "remove" on each). The draft shows no ⚠ weak-evidence flags; these come from reading the quotes against the labels:

| Item | Quote | Why |
|---|---|---|
| D2 #3 and R2 #3 | "Kasparro** is an emerging AI brand intelligence and SEO platform" | A neutral description, not an unfavourable one (the same kind of quote was removed from v1) |
| D2 #6 | "Publicly available enterprise user feedback ... is currently limited" | From H2-012-gemini, which the candidate decided is **not** negative (fresh_review_log.jsonl) |

Optional: D1 #4 "If you already use modern SEO suites (like Semrush or Google Search Console)" is a conditional clause; it does name a competitor, so keeping it is defensible.

After the removals, D1 keeps 6 quotes, D2 4, D3 6, R1 3, R2 2 and R3 3. Every remaining quote from a labelled case agrees with its human label; the three new D1 quotes (evidence-v3) come from unlabelled unbranded answers, all verbatim (evidence check: no problems).

**Analyst notes** (paste):

> 1) Method: labels come from classify-v2, promoted on 29 Oct 2026 after evaluation (EVALUATION.md). On the independent holdout2 set it cut "recommended" false positives from 10 to 2 compared with classify-v1, which produced the approved report 7d80ca70. Rates are therefore not comparable with that report: recommended 12/149 vs 40/148 and negative 23/149 vs 30/148 mainly reflect the method change, not a change in the engines' answers (same 31 Jul 2026 capture); only the recommended change lies outside the 95% intervals (report comparison). 2) Entity confusion (9/74 branded answers) is now the third diagnostic. It remains a lower bound, because product misattribution (evaluation case H06) is not detected. 3) The negative count is uncertain: on holdout2, 3 of classify-v2's 6 negative calls matched the human label, so 23/74 may overstate unfavourable framing. One quote whose answer the human labels treat as not negative was removed. 4) 1 of 150 answers failed validation (non-verbatim quote) and is excluded from all rates, not scored as zero. 5) A live re-run of 38 labelled cases reproduced every label in at least 37 of 38 cases. All counts come from one historical capture; no causal or ranking claims are made.

Then **submit** version 1 (as analyst). The review deadline is set to 72 hours.

## Reviewer checklist (signed in as reviewer)
- Open **Compare with another report** (defaults to the approved `7d80ca70`; CLI: `python -m app.cli report-diff 7d80ca70-6538-4f7f-b097-70b989f6b761 6edb78b8-2db6-4633-b9c7-f1a6aa8b8e4f`). Expected: the method changed (prompt, report generator) on the same capture; only *recommended* moves beyond the 95% intervals (40/148 → 12/149); *negative* (30/148 → 23/149) and *entity confusion* (8 → 9) are within them.
- Do the key findings match the scorecard? D1 0/75 unbranded, D2 23/74, D3 9/74 (identical in both drafts).
- Is there no ⚠ weak-evidence flag left?
- Do the analyst notes disclose the method change and the uncertainty in the negative count?
- Remedies: R3 is low effort and validated by a re-run; R1 and R2 are framed as investigations, not guaranteed outcomes.
- Decide approve or reject with a comment. Export works only after approval, and the export carries the content hash.
- After approving and exporting, verify the file: `python -m app.verify_export <export.json> --answers assignment/data/responses.jsonl` (all checks should PASS).

Possible reviewer comment if approving (edit freely): "Approved. classify-v2 draft with weak and label-inconsistent quotes removed; the method change and its effect on rates are disclosed in the analyst notes; content hash checked before approval."

## Notes
- Restart the console server so it runs the promoted code: stop the running `uvicorn` processes and start `python -m uvicorn app.main:create_app --factory --port 8000`. `/health` should then show prompt `classify-v2`. The draft itself is in the database and displays either way.
- The competitor count fix (59bc7e5) merges "Otterly"/"OtterlyAI" (16), as well as "Dageno"/"Dageno AI" and "Scrunch"/"Scrunch AI". The approved report counted Otterly in two rows (12 + 4). That report is unchanged; this note records the discrepancy.
- `6edb78b8` was created with `python -m app.cli draft-report f144fd60-c2aa-4291-aff7-4a1147a6fa75` after a backup (`var/backups/answerscope_pre_report_v3_draft.db`); nothing was deleted.
- Backup of the main DB before any v2 change: `var/backups/answerscope_pre_v2_promotion.db`. Two earlier v2 drafts were removed by restoring this backup: `01f0ff76`, made before the competitor-count fix, and `b4b9c5fd`, made before the report-v2 version bump. Neither was edited or submitted. The restores are the only DB changes other than the new analysis and draft; both approved versions are intact.
