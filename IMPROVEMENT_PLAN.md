# Improvement plan (sprint, 29 Oct 2026)

The approved submission is protected: git tag `submission-v1` (commit `0abc2c7`). The archive `../answerscope_submission.zip` is byte-identical to `git archive` of that commit. `labels_v2`, `labels_v3`, the 150 classify-v1 recordings, `outputs/approved_report_export.json` and `evaluation/results/eval_report.md` are unchanged; hashes are pinned in tests and in `evaluation/compare.py`. All sprint work is additive: a candidate prompt `classify-v2`, new label sets and a separate comparison report.

## 1. Evidenced failure modes (classify-v1)

The sources are `evaluation/results/eval_results.json` (per-case predictions and rationales) and the raw outputs in `replay/classify_v1/<response_id>.json`. "Observed" means read from those files; "hypothesis" means inferred.

| # | Failure mode | Cases (observed) | The model's own evidence (observed) | Type |
|---|---|---|---|---|
| FM1 | A neutral description or positioning is treated as a recommendation | H05, H10 | H05: "Kasparro operates as an AI-native SEO and Brand Intelligence platform…"; H10: "Kasparro positions itself as an AI visibility platform…" | model error (H05 and H10 are labelled `recommended` ambiguous) |
| FM2 | An affirmative factual answer or a price is treated as an endorsement | H07, H06 | H07: "The answer is yes, based on its positioning there is no indication that it is US-only"; H06: "Kasparro's 14-day AI Revenue Diagnostic starts at ₹49,999" | model error |
| FM3 | The answering assistant's own offer is quoted as a recommendation of Kasparro | H11 | "If you are considering this audit, I can: Detail the specific actions…" | model error; the quote's subject is not Kasparro |
| FM4 | Statements about a misidentified entity are counted as negative about Kasparro | H01 | negative evidence: "it brings inherent risks regarding LLM terms of service (ToS) and data security" about "Kasparro (an AI coding assistant)" | model error against rubric R-I2 (label marked ambiguous) |
| FM5 | Product misattribution is missed | H06 | entity_confusion = false; the price is cited only to revenuepulseai.com (MC-01) | prompt does not cover rubric C3 |
| FM6 | Weak quotes reach the report | approved report v1 | The candidate removed 5 quotes during review. D2: a neutral description and a category-level doubt. D3: "positions itself as…", a conditional example, and "Choose Alternatives if…" | downstream effect of FM1/FM2, plus evidence selection |

Other error types, checked and separated out:
* **Rubric ambiguity.** 3 of the 5 recommendation false positives (H05, H07, H10) are on labels marked ambiguous. With ambiguous labels excluded, recommendation precision is 0.50, not 0.29.
* **Evidence-span / matcher errors.** H11 originally failed on a quote crossing a list bullet (F5, fixed earlier). There are no other matcher errors in the final split.
* **Parser errors.** None: all 14 final-split outputs parsed. The 2 full-pack failures are non-verbatim quotes (EVALUATION.md).
* **Evaluation-implementation defects found earlier and fixed:** S01/S02 had no recordings (`replay_missing`); competitor spelling variants were counted separately; remedy text ended with a double full stop.
* **Same examples and semantics?** Yes. Baseline and model run on identical cases, and both outputs pass through the same validator. `mentioned` is lexical for both.

## 2. Proposed changes, risks and validation

| Change | Addresses | Risk | Validation |
|---|---|---|---|
| **classify-v2 prompt**: decide `recommendation_type` first (explicit_endorsement / suitability_claim / neutral_description / factual_answer / negative_or_alternative / not_applicable); recommended only for the first two; assistant offers, prices, features and sign-up are never recommendation evidence; misidentified-entity statements are not negative | FM1–FM4 | Under-calling true recommendations (lower recall); the examples paraphrase original-holdout answers, so that holdout cannot confirm v2 | dev (tuning), then the fresh **holdout2**, frozen before any v2 run |
| **Deterministic rules (v2 only)**: `kasparro_recommended` must agree with `recommendation_type`; recommendation evidence must sit in a sentence that names Kasparro | FM3, inconsistent outputs | More retries or failures if the model quotes a fragment | unit tests (`tests/test_classify_v2.py`), failure counts in the comparison |
| **evidence-v2**: advisory warnings per evidence item (short quote, label disagreement, quote outside a Kasparro sentence, answer also confused); drafts prefer quotes without warnings | FM6 | Warnings are heuristics; they flag, they do not decide | `tests/test_review.py`; console shows the flags |
| **Fresh labelled data** (fresh-v1: 12 dev + 24 holdout2 answers from 12 never-labelled prompts, split by prompt, labelled blind to predictions and hash-frozen, commit `b932b1e`) | the original holdout is spent | AI-drafted labels (pending candidate review); few recommendation positives | `tests/test_fresh_cases.py`; reported separately |
| **FM5 not addressed** | – | Teaching "price cited only to another domain = confusion" would also flag T02-like answers that cite third-party pages for real Kasparro features | documented limitation |

What would count as success: on holdout2, classify-v2 has fewer recommendation false positives than classify-v1, without new failures or losses on negative and entity confusion. holdout2 has very few true recommendations, so it can show **precision and specificity**, not recall. Any claim of superiority stays conditional on that small n.

## 3. Outcome (measured, `evaluation/results/compare_report.md`)

| Failure mode | classify-v2 result | Evidence |
|---|---|---|
| FM1 neutral description → recommended | Fixed on the measured cases | holdout2: recommended FP 10 → 2; dev 4 → 1; SR02 (neutral) correct |
| FM2 affirmative factual answer / price → recommended | Fixed on the measured cases | final_seen H06, H07, H10 no longer recommended; SR03 correct |
| FM3 assistant offer as evidence | Fixed, enforced by a rule | H11 correct; `test_regression_h11_…`; SR10 correct |
| FM4 misidentified-entity statements → negative | **Not fixed** | H01 still negative under v2 (final_seen) |
| FM5 product misattribution | Partly addressed (reviewer advisory, 29 Oct 2026) | H06 entity_confusion still missed by both prompts. `claims-v1` (`app/services/claims.py`) flags a Kasparro price cited only to non-Kasparro domains, beside the report (never counted, never a label). On the pack: 3 of 75 branded answers state a Kasparro price; 2 flagged (H06, and an unlabelled deal-size claim cited to a job site); the third has no inline link. Too few cases for precision or recall. |
| FM6 weak report evidence | Mitigated | evidence-v2 warnings + preference for strong quotes; root cause (label precision) improved by v2 |
| New: confused entity recommended (dev D-017-gemini) | Fixed, enforced by a rule (R-I3) | `test_regression_dev_017_gemini_…` |
| New: injected instruction steers v2 (SR08) | Contained, not fixed | the validator rejected all 3 attempts, so the case is an explicit failure, not a wrong label |

Regressions: negative recall on holdout2 4/4 → 3/4 (ambiguous labels). Entity confusion on holdout2 remains 1 of 4 for v2.

## 4. Next steps (proposed, not implemented)

Implementing these now would mean tuning against holdout2 after seeing its results, so they are left for a later round with a new holdout.

| Open item | Proposal | How to validate honestly |
|---|---|---|
| FM4: negative statements about a misidentified entity (H01) | Code rule like R-I3: when `entity_confusion` is true, negative evidence must sit in a sentence that names Kasparro *as Kasparro* (not inside the confused description), or the label is rejected | Label a new prompt-disjoint holdout (holdout3) first, freeze it, then compare v2 vs v3 |
| FM5: product misattribution (H06) | Implemented for prices as `claims-v1` (advisory). Extending it to product names and features needs a product inventory from kasparro.com | Label more C3 cases on a new holdout; report flags per label with Wilson CIs |
| Entity confusion recall (holdout2 1/4) | Tried 29 Oct 2026 and **not adopted**: a lexical "mentions Kaspr" flag. On labelled sets it agrees with 7 of 8 human confusion labels, but the 3 full-pack v2 answers it would add are correct disambiguations ("Kasparro … not Kaspr"), so it would only add false alarms | Needs a semantic rule (does the answer *describe* Kasparro as Kaspr?), validated on a new holdout |
| Low recommendation recall evidence | holdout2 has very few true recommendations; collect or label more positive cases | Report recall with Wilson CIs only once n ≥ 10 positives |
| Run-to-run variance | `evaluation/stability.py`, one live re-run each: v1 flipped 1 of 37 `recommended` (H2-018-aimode), v2 flipped 1 of 38 `negative` (H2-018-chatgpt) | Repeat with `--runs 3`; report flip rate per label |
| Promotion of classify-v2 | Requires candidate review of the fresh-v1 labels and a newly reviewed report; the approved v1 report stays as submitted | Reviewer workflow (submit → approve) on a v2 draft |
