# Changelog

Every version identifier that can change a result, and what changed it. Runs, reports and exports record these identifiers in their provenance, and `/health` reports the running ones. Dates are 2026. Commit hashes link the change to the code.

## Version identifiers in use

| Identifier | Current | Kind | Changes results? |
|---|---|---|---|
| Prompt | `classify-v2` (default since 29 Oct); `classify-v1` still registered | Model contract + deterministic rules | Yes: labels |
| Score | `vis-v1` | Weights | Yes: scores |
| Categories | `cat-v1` | Branded/unbranded and topic rules | Yes: segments |
| Report generator | `report-v3` | Draft diagnostics and evidence selection | Draft content only |
| Evidence policy | `evidence-v3` | Advisory quote warnings and quote preference | Draft evidence and warnings |
| Claim check | `claims-v1` | Reviewer advisory (possible product misattribution) | No: advisory only |
| Report schema | `report-v1` | Content structure | No |
| Labels | `labels-v3` (17 cases); `fresh-v2` (36 cases) | Human/AI labels, frozen and hash-pinned | Evaluation only |

## 29 Oct: engineering sprint, after the approved submission (tag `submission-v1`)

The approved report `7d80ca70`, `outputs/approved_report_export.json`, `outputs/analysis_output.json`, `evaluation/results/eval_report.md`, `labels_v2` and `labels_v3` are unchanged since the tag.

### Prompt
- **classify-v2** (d2eeae6, cef56e9, ff32628; frozen at tag `classify-v2-frozen`). An explicit `recommendation_type` must agree with `kasparro_recommended`. Recommendation evidence must sit in a sentence that names Kasparro. A confused entity cannot be recommended (rule R-I3). Effect on holdout2: recommended false positives 10 → 2 (EVALUATION.md).
- **Promoted to the default** (b50343e) by the candidate's decision. `run_eval` and the keyword baseline stay on the classify-v1 contract, so the evaluation of record reproduces.

### Report generator and evidence
- **evidence-v2** (d2eeae6): advisory warnings per quote (very short quote, label disagreement, quote not in a Kasparro sentence, confused answer). Drafts prefer quotes without warnings.
- **report-v2** (59bc7e5, 81f7727): competitor names with or without an "AI" suffix are counted once (Otterly 12 + 4 → 16). The approved v1 report keeps its split count; the discrepancy is documented.
- **report-v3 / evidence-v3** (3333a51): the unbranded diagnostic also prefers strong competitor quotes, and assistant follow-up offers ("Would you like…") are flagged. On the v2 analysis, flagged quotes in the draft went from 4 to 0, with identical metrics.
- **claims-v1** (8b6598b): reviewer advisory for a Kasparro price cited only to non-Kasparro domains (failure mode FM5, case H06). It is never counted in a diagnostic.

### Review workflow and tools
- Review deadline on submit (bee5c58): overdue versions are flagged and never auto-approved.
- `draft-report` CLI (294acdf). The demo image seeds an unsubmitted draft.
- Report comparison (ecedf1a, e945679): API, CLI and console. It separates method changes from data changes and marks rate changes by 95% interval overlap.
- Offline export verifier (d19f484): `python -m app.verify_export`.
- `backup-db` CLI (5212152).
- Readable report: `python -m app.render_export` and `GET /reports/{id}/export.md` (console: "Download readable report"). It renders only an export that verifies (93fe477, 2ff0531). `outputs/approved_report.md` is the approved v1 report rendered this way.
- `/health` lists every version above (2199d63).

### Evaluation
- fresh-v1 (b932b1e): 36 answers, AI-drafted labels blind to predictions, frozen before any v2 run.
- fresh-v2 (593b549): fresh-v1 plus the candidate's decisions on the AI audit (one label changed). `fresh_review` refuses to overwrite a frozen set (d69276b).
- Three-way comparison, stability study and synthetic robustness fixtures (2d0876f, 7430a5b, a6ac8b8, 1893a14).

### Not adopted
- A lexical "mentions Kaspr" entity-confusion flag (IMPROVEMENT_PLAN.md). The answers it would add are correct disambiguations.

## 28–29 Oct: original submission (tag `submission-v1`)
`classify-v1`, `vis-v1`, `cat-v1`, report generator `report-v1`, `labels-v3`. Approved report `7d80ca70` v1. See DECISION_NOTE.md and EVALUATION.md.
