# Evaluation report

Generated 2026-10-28T17:41:22+00:00 | labels `labels-v2-proposed` | prompt `classify-v1` | score `vis-v1` | baseline `baseline-v1`

**Model system:** provider `stub`, execution mode `stub`, model `stub-baseline-v1`.

> STUB MODE: the 'model' column is the deterministic baseline. Model quality is NOT measured.

Final check = holdout + synthetic cases (never used for prompt tuning). Tuning cases are reported separately and should not be read as generalisation.

## Final split (14 cases: H01, H02, H03, H04, H05, H06, H07, H08, H09, H10, H11, H12, S01, S02)

| System | Eligible | Succeeded | Failed | Skipped |
|---|---|---|---|---|
| baseline | 14 | 14 | 0 | 0 |
| model | 14 | 14 | 0 | 0 |

**Per-label metrics (all labels)**

| Label | System | Positives | TP | FP | FN | TN | Precision | Recall | F1 | Agreement |
|---|---|---|---|---|---|---|---|---|---|---|
| mentioned | baseline | 11 | 11 | 0 | 0 | 3 | 1.00 | 1.00 | 1.00 | 1.00 |
| mentioned | model | 11 | 11 | 0 | 0 | 3 | 1.00 | 1.00 | 1.00 | 1.00 |
| recommended | baseline | 2 | 2 | 1 | 0 | 11 | 0.67 | 1.00 | 0.80 | 0.93 |
| recommended | model | 2 | 2 | 1 | 0 | 11 | 0.67 | 1.00 | 0.80 | 0.93 |
| negative | baseline | 4 | 1 | 0 | 3 | 10 | 1.00 | 0.25 | 0.40 | 0.79 |
| negative | model | 4 | 1 | 0 | 3 | 10 | 1.00 | 0.25 | 0.40 | 0.79 |
| entity_confusion | baseline | 3 | 1 | 0 | 2 | 11 | 1.00 | 0.33 | 0.50 | 0.86 |
| entity_confusion | model | 3 | 1 | 0 | 2 | 11 | 1.00 | 0.33 | 0.50 | 0.86 |

**Per-label metrics (ambiguous labels excluded)**

| Label | System | Positives | TP | FP | FN | TN | Precision | Recall | F1 | Agreement |
|---|---|---|---|---|---|---|---|---|---|---|
| mentioned | baseline | 11 | 11 | 0 | 0 | 3 | 1.00 | 1.00 | 1.00 | 1.00 |
| mentioned | model | 11 | 11 | 0 | 0 | 3 | 1.00 | 1.00 | 1.00 | 1.00 |
| recommended | baseline | 2 | 2 | 1 | 0 | 8 | 0.67 | 1.00 | 0.80 | 0.91 |
| recommended | model | 2 | 2 | 1 | 0 | 8 | 0.67 | 1.00 | 0.80 | 0.91 |
| negative | baseline | 2 | 0 | 0 | 2 | 9 | n/a | 0.00 | 0.00 | 0.82 |
| negative | model | 2 | 0 | 0 | 2 | 9 | n/a | 0.00 | 0.00 | 0.82 |
| entity_confusion | baseline | 3 | 1 | 0 | 2 | 11 | 1.00 | 0.33 | 0.50 | 0.86 |
| entity_confusion | model | 3 | 1 | 0 | 2 | 11 | 1.00 | 0.33 | 0.50 | 0.86 |

| System | Competitor precision | Competitor recall | Score exact | Score MAE | Position exact |
|---|---|---|---|---|---|
| baseline | 1.00 (tp 14, fp 0) | 0.88 (fn 2) | 9/14 | 12.14 | 0/1 |
| model | 1.00 (tp 14, fp 0) | 0.88 (fn 2) | 9/14 | 12.14 | 0/1 |

## Tuning split (5 cases: T01, T02, T03, T04, T05)

| System | Eligible | Succeeded | Failed | Skipped |
|---|---|---|---|---|
| baseline | 5 | 5 | 0 | 0 |
| model | 5 | 5 | 0 | 0 |

**Per-label metrics (all labels)**

| Label | System | Positives | TP | FP | FN | TN | Precision | Recall | F1 | Agreement |
|---|---|---|---|---|---|---|---|---|---|---|
| mentioned | baseline | 3 | 3 | 0 | 0 | 2 | 1.00 | 1.00 | 1.00 | 1.00 |
| mentioned | model | 3 | 3 | 0 | 0 | 2 | 1.00 | 1.00 | 1.00 | 1.00 |
| recommended | baseline | 1 | 1 | 0 | 0 | 4 | 1.00 | 1.00 | 1.00 | 1.00 |
| recommended | model | 1 | 1 | 0 | 0 | 4 | 1.00 | 1.00 | 1.00 | 1.00 |
| negative | baseline | 2 | 2 | 0 | 0 | 3 | 1.00 | 1.00 | 1.00 | 1.00 |
| negative | model | 2 | 2 | 0 | 0 | 3 | 1.00 | 1.00 | 1.00 | 1.00 |
| entity_confusion | baseline | 1 | 1 | 0 | 0 | 4 | 1.00 | 1.00 | 1.00 | 1.00 |
| entity_confusion | model | 1 | 1 | 0 | 0 | 4 | 1.00 | 1.00 | 1.00 | 1.00 |

**Per-label metrics (ambiguous labels excluded)**

| Label | System | Positives | TP | FP | FN | TN | Precision | Recall | F1 | Agreement |
|---|---|---|---|---|---|---|---|---|---|---|
| mentioned | baseline | 3 | 3 | 0 | 0 | 2 | 1.00 | 1.00 | 1.00 | 1.00 |
| mentioned | model | 3 | 3 | 0 | 0 | 2 | 1.00 | 1.00 | 1.00 | 1.00 |
| recommended | baseline | 1 | 1 | 0 | 0 | 4 | 1.00 | 1.00 | 1.00 | 1.00 |
| recommended | model | 1 | 1 | 0 | 0 | 4 | 1.00 | 1.00 | 1.00 | 1.00 |
| negative | baseline | 2 | 2 | 0 | 0 | 3 | 1.00 | 1.00 | 1.00 | 1.00 |
| negative | model | 2 | 2 | 0 | 0 | 3 | 1.00 | 1.00 | 1.00 | 1.00 |
| entity_confusion | baseline | 1 | 1 | 0 | 0 | 4 | 1.00 | 1.00 | 1.00 | 1.00 |
| entity_confusion | model | 1 | 1 | 0 | 0 | 4 | 1.00 | 1.00 | 1.00 | 1.00 |

| System | Competitor precision | Competitor recall | Score exact | Score MAE | Position exact |
|---|---|---|---|---|---|
| baseline | 1.00 (tp 8, fp 0) | 1.00 (fn 0) | 5/5 | 0.00 | 0/0 |
| model | 1.00 (tp 8, fp 0) | 1.00 (fn 0) | 5/5 | 0.00 | 0/0 |

## Per-case disagreements with expected labels

| Case | Split | System | Status | Label differences | Score (pred/exp) |
|---|---|---|---|---|---|
| H01 | holdout | baseline | succeeded | entity_confusion: exp True, got False | 40/20 |
| H01 | holdout | model | succeeded | entity_confusion: exp True, got False | 40/20 |
| H02 | holdout | baseline | succeeded | negative: exp True, got False (ambiguous) | 40/10 |
| H02 | holdout | model | succeeded | negative: exp True, got False (ambiguous) | 40/10 |
| H06 | holdout | baseline | succeeded | entity_confusion: exp True, got False | 40/20 |
| H06 | holdout | model | succeeded | entity_confusion: exp True, got False | 40/20 |
| H07 | holdout | baseline | succeeded | negative: exp True, got False | 40/10 |
| H07 | holdout | model | succeeded | negative: exp True, got False | 40/10 |
| S02 | synthetic | baseline | succeeded | recommended: exp False, got True; negative: exp True, got False | 80/10 |
| S02 | synthetic | model | succeeded | recommended: exp False, got True; negative: exp True, got False | 80/10 |

## Score arithmetic (independent check)

Hand-computed expected scores vs `scoring.score()` on expected labels: 19 checked, 0 mismatches.


## Limits of this evaluation

- 17 real + 2 synthetic cases: metrics have wide uncertainty; one label flip moves precision/recall a lot.
- Labels were drafted by the AI coding assistant from full answer text and need candidate review; a single labeller means no inter-annotator agreement.
- 'Recommended' is the most ambiguous label; ambiguous labels are reported both included and excluded.
- One model run only; replay reproduces it but cannot show variance. Citation support is not evaluated.
- The checker verifies that evidence exists and carries the claimed label; it cannot judge whether a hypothesis is correct. No LLM grades its own output here.
