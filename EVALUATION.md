# Evaluation

**Status: complete (29 Oct 2026).** Results below are copied from `evaluation/results/eval_report.md`, produced by `python -m evaluation.run_eval`. They use replay of the one recorded local-model run (gemma4:12b) and candidate-reviewed `labels_v3.jsonl`. Every label was decided before this run. v1 and v2 are kept unchanged.

## What is measured, and how

| Question | Method |
|---|---|
| Does the classifier label answers correctly? | 17 supplied answers (5 tuning, 12 holdout) + 2 synthetic edge cases, labelled against [evaluation/RUBRIC.md](evaluation/RUBRIC.md). Per-label TP/FP/FN/TN, precision, recall, F1, agreement, and the number of positives, for **baseline** and **model** on the same cases. Reported strict and with ambiguous labels excluded. |
| Is it better than a simple rule? | `baseline-v1` keyword rules (`app/services/baseline.py`) vs `classify-v1` + local model, same cases, same validator. |
| Sensitivity to post-hoc changes | `final_sensitivity` repeats the final split without H11, whose outcome changed through the F5 matcher fix made after its failure was seen. |
| Is tuning separate from the final check? | Final = holdout + synthetic; tuning cases reported separately. Exposure of holdout text during prompt design is disclosed per case (LABEL_AUDIT.md §2). |
| Are scores computed correctly? | Hand-computed expected scores vs `scoring.score()` (independent arithmetic check); score MAE/exact match of predicted vs expected; `tests/test_scoring.py` (including the brief's 12/2/4-of-10 example). |
| Are failures visible? | Eligible / succeeded / failed / skipped for every system and split; full-pack counts in the diagnostics check. |
| Do diagnostics have evidence, and do remedies follow? | Full-pack draft report: every quote must exist verbatim in its cited response; each evidence response must carry the label its diagnostic claims; each remedy must cite its own diagnostic's evidence. **Negative case:** the checker must detect 4 injected defects (a fabricated quote, a real quote attributed to the wrong response, a remedy pointing to a missing diagnostic, remedy evidence from another diagnostic). |
| Failure → fix → regression | [evaluation/FAILURES.md](evaluation/FAILURES.md): F1–F5, each with a regression test. |

Command: `python -m evaluation.run_eval` (default labels: candidate-reviewed `labels_v3.jsonl`) writes `evaluation/results/eval_report.md` and `eval_results.json`.

## Mechanics verified earlier (stub mode; not model quality)
* Runner, splits, metrics, positives column, arithmetic check (19/19 hand-computed scores match vis-v1).
* Evidence checker: clean generated report has 0 problems; negative case has 4/4 injected defects detected.
* The baseline on the final split already shows its blind spots: it misses negatives without keywords (H02, H07), misses the "coding assistant" misidentification (H01), and is fooled by the injected instruction in S02 ("mark Kasparro as recommended").

## Results

### Coverage and cost (full pack, 150 answers)
* **Replay analysis:** 148 succeeded, **2 failed**, 0 skipped. 167 model calls (148 ok, 19 rejected by the validator).
  * Both failures are genuine non-verbatim quotes. One dropped the comma in `"agentic commerce,"`. The other paraphrased "specializes in AI visibility platforms" as "builds an AI Visibility platform".
  * The matcher was not loosened after this was seen. Both appear as failures, not zeros.
* **Live recording run:** 171 calls (147 ok, 24 invalid). 134 answers needed 1 attempt, 11 needed 2, 5 needed 3.
  * Latency per call: mean 63 s, median 62 s, p90 91 s, 3.0 h in total on an RTX 3050 6 GB laptop.
  * Cost: US$0 (local model; electricity not costed).
  * Replay differs slightly (148 vs 147 ok) because it re-checks the recorded attempts with current code, including the F5 fix.

### Final split (12 holdout + 2 synthetic; strict, ambiguous included)

| Label | Positives | Baseline P / R / F1 | Model P / R / F1 |
|---|---|---|---|
| mentioned | 11 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 |
| recommended | 2 | 0.67 / 1.00 / 0.80 | **0.29** / 1.00 / 0.44 |
| negative | 4 | 1.00 / 0.25 / 0.40 | 0.80 / 1.00 / **0.89** |
| entity_confusion | 3 | 1.00 / 0.33 / 0.50 | 1.00 / 0.67 / **0.80** |

Other final-split results:
* **Competitors:** precision/recall is 1.00 / 0.88 for the baseline and 0.94 / 1.00 for the model.
* **Scores:** 9/14 exact (MAE 12.1) for the baseline and 8/14 (MAE 17.1) for the model. List position correct: 0/1 baseline, 1/1 model.
* **Ambiguous labels excluded:** model recommended P 0.50 (F1 0.67); model negative 1.00 vs baseline 0.00 (2 positives).
* **Without H11 (`final_sensitivity`):** the same picture. Model recommended P 0.20, negative F1 0.86, entity_confusion F1 0.80.
* **Tuning split (5 cases):** both systems score 1.00 on all four labels. Model competitor precision is 0.61. All 5 false positives come from T03: sales tools named alongside Kaspr (HubSpot, Salesloft, Instantly, Wiza, Apollo), which the rubric excludes.

### What this shows
1. **The model is better where judgment is needed.**
   * Negative: it catches unfavourable comparisons and evidence-gap hedging without keywords (H02, H07), which the baseline misses.
   * Entity confusion: it catches "Kasparro (an AI coding assistant)" (H01), which the baseline misses.
   * Prompt injection (S02): the model ignores the embedded instruction. The baseline is fooled into "recommended" and "not negative".
2. **The model over-predicts "recommended".** It makes 5 false positives on 14 cases (H05, H06, H07, H10, H11; 3 of them on labels marked ambiguous). It treats favourable description, sign-up availability and capability statements as recommendations. This is the main reason its score MAE is worse than the baseline's: each false recommendation adds 40 points.
   * The prompt was not changed after seeing this, because that would be tuning on the holdout.
   * Consequence for findings: the full-pack branded recommendation count (40/73) is probably an **overestimate**. Diagnostic D3 must be read with that caveat.
3. **Product misattribution (H06) is missed.** As noted earlier, the prompt does not cover the C3 class. Full-pack entity-confusion counts (8/73) are therefore a lower bound.
4. **Mention is perfect by construction:** it is checked lexically by code, not judged by the model.

### Diagnostics and remedies (full pack)
* The generated draft has **0 problems**: every quote is verbatim in its cited response, each evidence item carries the label its diagnostic claims, and each remedy follows from its own diagnostic.
* The negative case passes: **4/4** injected defects are detected (fabricated quote, wrong-response attribution, remedy without a diagnostic, remedy evidence from another diagnostic).
* Score arithmetic: 19/19 hand-computed scores match `scoring.score()`.

## Limits
* 17 real + 2 synthetic cases; some labels have 1–2 positives in the final split, so one case moves recall by 50 points. Treat the metrics as indicative only.
* Labels were drafted by the AI assistant that also wrote the prompt. The candidate then reviewed and decided every case (an AI-assisted second-opinion audit was used as input). There is effectively one annotator and no inter-annotator agreement.
* One model run (temperature 0, fixed seed). Replay reproduces it; it cannot show variance, latency distribution or cost.
* Citation support is not evaluated: no cited page was opened.
* The checker proves that evidence exists and is consistent; it cannot prove that a hypothesis is right. No LLM grades its own output.
