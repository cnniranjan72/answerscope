# Evaluation

**Status: method complete; final results PENDING.** They need (1) the full local-model recording (in progress) and (2) frozen labels (`labels_v2.jsonl`, frozen 28 Oct 2026 after candidate adjudication). No model-quality number in this repository should be quoted until this section is filled from an actual `run_eval` output.

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

Command: `python -m evaluation.run_eval` (default labels: frozen `labels_v2.jsonl`) writes `evaluation/results/eval_report.md` and `eval_results.json`.

## Mechanics already verified (stub mode; not model quality)
* Runner, splits, metrics, positives column, arithmetic check (19/19 hand-computed scores match vis-v1).
* Evidence checker: clean generated report has 0 problems; negative case has 4/4 injected defects detected.
* The baseline on the final split already shows its blind spots: it misses negatives without keywords (H02, H07), misses the "coding assistant" misidentification (H01), and is fooled by the injected instruction in S02 ("mark Kasparro as recommended").

## Results
_Pending; filled from the frozen-label run._

## Limits
* 17 real + 2 synthetic cases; some labels have 1–2 positives in the final split, so one case moves recall by 50 points. Treat the metrics as indicative only.
* Labels were drafted by the AI assistant that also wrote the prompt, then adjudicated by the candidate on disputed cases. There is one annotator and no inter-annotator agreement.
* One model run (temperature 0, fixed seed). Replay reproduces it; it cannot show variance, latency distribution or cost.
* Citation support is not evaluated: no cited page was opened.
* The checker proves that evidence exists and is consistent; it cannot prove that a hypothesis is right. No LLM grades its own output.
