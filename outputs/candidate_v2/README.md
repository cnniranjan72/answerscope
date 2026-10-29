# classify-v2 full-pack output (NOT approved)

Produced while classify-v2 was the candidate. It was promoted to the default on 29 Oct 2026; this file is still unreviewed. The v2 report under review is `6edb78b8` (claude-code/V2_REPORT_REVIEW.md).

`analysis_output.json` is a replay of the full 150-answer pack under the **candidate** prompt `classify-v2`
(analysis `1124fd24`, model `gemma4:12b`, temperature 0, seed 7, recordings in `replay/classify_v2/`).
It has not been reviewed or approved. The approved deliverable is still `outputs/approved_report_export.json`
(classify-v1). The `note` field inside the file is the generic draft note written by `write-output`;
for this file, "the approved report export" refers to the classify-v1 report, not to this run.

| Full pack (all 150) | classify-v1 (approved run) | classify-v2 (candidate) |
|---|---|---|
| succeeded / failed | 148 / 2 | 149 / 1 |
| mentioned | 70 / 148 | 71 / 149 |
| recommended | 40 / 148 (0.27) | 12 / 149 (0.08) |
| negative | 30 / 148 | 23 / 149 |
| entity confusion | 8 / 148 | 9 / 149 |
| mean score (vis-v1) | 24.9 | 18.7 |
| draft D3 | "some engines present it as a fit" (branded_win) | "Engines confuse Kasparro with other entities" |

These are model predictions on mostly unlabelled answers, not accuracy figures. Accuracy is measured only on labelled
splits in `evaluation/results/compare_report.md` (holdout2: recommended false positives 10 → 2, MAE 20.0 → 10.8).
The fall in `recommended` from 40 to 12 is consistent with v1's measured over-calling, but part of it may be
lost true recommendations: holdout2 has too few positives to measure recall. Remaining failure: `4b70d3c9`
(non-verbatim quote, also failed under v1).

Reproduce: `DATABASE_PATH=var/v2_live.db python -m app.cli analyse --provider replay --prompt-version classify-v2`,
then `write-output <analysis_id> --out outputs/candidate_v2/analysis_output.json --active-minutes 170`.
