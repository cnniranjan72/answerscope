# Comparison report: baseline vs classify-v1 vs classify-v2

Generated 2026-10-29T09:07:23+00:00 | labels {'labels_v3.jsonl': 'a893038eb00bd4c7', 'fresh_v2.jsonl': 'e5efcf2ddc070908'} | score `vis-v1` | v1 `replay` | v2 `replay`

> **Read holdout2 for independent evidence.** final_seen was inspected while designing classify-v2; dev was used to tune it. Labels: labels-v3 (candidate-reviewed) and fresh-v2 (fresh-v1 after an AI audit; the candidate decided the 4 audit items, changing D-017-aimode only; see fresh_review_log.jsonl). Intervals are Wilson 95% on tiny counts: treat them as a warning about uncertainty, not as significance tests.

## tuning (5 cases)

| System | Succeeded | Failed | Score exact | Score MAE |
|---|---|---|---|---|
| baseline | 5 | 0 | 5/5 | 0.0 |
| classify-v1 | 5 | 0 | 5/5 | 0.0 |
| classify-v2 | 5 | 0 | 5/5 | 0.0 |

**all labels** (TP/FP/FN/TN = confusion matrix; P and R with Wilson 95% interval)

| Label | System | Pos | TP | FP | FN | TN | Precision | Recall | F1 |
|---|---|---|---|---|---|---|---|---|---|
| mentioned | baseline | 3 | 3 | 0 | 0 | 2 | 1.0 [0.44, 1.0] | 1.0 [0.44, 1.0] | 1.0 |
| mentioned | classify-v1 | 3 | 3 | 0 | 0 | 2 | 1.0 [0.44, 1.0] | 1.0 [0.44, 1.0] | 1.0 |
| mentioned | classify-v2 | 3 | 3 | 0 | 0 | 2 | 1.0 [0.44, 1.0] | 1.0 [0.44, 1.0] | 1.0 |
| recommended | baseline | 1 | 1 | 0 | 0 | 4 | 1.0 [0.21, 1.0] | 1.0 [0.21, 1.0] | 1.0 |
| recommended | classify-v1 | 1 | 1 | 0 | 0 | 4 | 1.0 [0.21, 1.0] | 1.0 [0.21, 1.0] | 1.0 |
| recommended | classify-v2 | 1 | 1 | 0 | 0 | 4 | 1.0 [0.21, 1.0] | 1.0 [0.21, 1.0] | 1.0 |
| negative | baseline | 2 | 2 | 0 | 0 | 3 | 1.0 [0.34, 1.0] | 1.0 [0.34, 1.0] | 1.0 |
| negative | classify-v1 | 2 | 2 | 0 | 0 | 3 | 1.0 [0.34, 1.0] | 1.0 [0.34, 1.0] | 1.0 |
| negative | classify-v2 | 2 | 2 | 0 | 0 | 3 | 1.0 [0.34, 1.0] | 1.0 [0.34, 1.0] | 1.0 |
| entity_confusion | baseline | 1 | 1 | 0 | 0 | 4 | 1.0 [0.21, 1.0] | 1.0 [0.21, 1.0] | 1.0 |
| entity_confusion | classify-v1 | 1 | 1 | 0 | 0 | 4 | 1.0 [0.21, 1.0] | 1.0 [0.21, 1.0] | 1.0 |
| entity_confusion | classify-v2 | 1 | 1 | 0 | 0 | 4 | 1.0 [0.21, 1.0] | 1.0 [0.21, 1.0] | 1.0 |

**ambiguous labels excluded** (TP/FP/FN/TN = confusion matrix; P and R with Wilson 95% interval)

| Label | System | Pos | TP | FP | FN | TN | Precision | Recall | F1 |
|---|---|---|---|---|---|---|---|---|---|
| mentioned | baseline | 3 | 3 | 0 | 0 | 2 | 1.0 [0.44, 1.0] | 1.0 [0.44, 1.0] | 1.0 |
| mentioned | classify-v1 | 3 | 3 | 0 | 0 | 2 | 1.0 [0.44, 1.0] | 1.0 [0.44, 1.0] | 1.0 |
| mentioned | classify-v2 | 3 | 3 | 0 | 0 | 2 | 1.0 [0.44, 1.0] | 1.0 [0.44, 1.0] | 1.0 |
| recommended | baseline | 1 | 1 | 0 | 0 | 4 | 1.0 [0.21, 1.0] | 1.0 [0.21, 1.0] | 1.0 |
| recommended | classify-v1 | 1 | 1 | 0 | 0 | 4 | 1.0 [0.21, 1.0] | 1.0 [0.21, 1.0] | 1.0 |
| recommended | classify-v2 | 1 | 1 | 0 | 0 | 4 | 1.0 [0.21, 1.0] | 1.0 [0.21, 1.0] | 1.0 |
| negative | baseline | 1 | 1 | 0 | 0 | 3 | 1.0 [0.21, 1.0] | 1.0 [0.21, 1.0] | 1.0 |
| negative | classify-v1 | 1 | 1 | 0 | 0 | 3 | 1.0 [0.21, 1.0] | 1.0 [0.21, 1.0] | 1.0 |
| negative | classify-v2 | 1 | 1 | 0 | 0 | 3 | 1.0 [0.21, 1.0] | 1.0 [0.21, 1.0] | 1.0 |
| entity_confusion | baseline | 1 | 1 | 0 | 0 | 4 | 1.0 [0.21, 1.0] | 1.0 [0.21, 1.0] | 1.0 |
| entity_confusion | classify-v1 | 1 | 1 | 0 | 0 | 4 | 1.0 [0.21, 1.0] | 1.0 [0.21, 1.0] | 1.0 |
| entity_confusion | classify-v2 | 1 | 1 | 0 | 0 | 4 | 1.0 [0.21, 1.0] | 1.0 [0.21, 1.0] | 1.0 |

**Errors by case (strict)**

| Label | System | False positives | False negatives |
|---|---|---|---|

classify-v2 recommendation_type distribution: {'neutral_description': 1, 'explicit_endorsement': 1, 'not_applicable': 2, 'negative_or_alternative': 1}

## dev (12 cases)

| System | Succeeded | Failed | Score exact | Score MAE |
|---|---|---|---|---|
| baseline | 12 | 0 | 7/12 | 12.5 |
| classify-v1 | 12 | 0 | 6/12 | 16.67 |
| classify-v2 | 12 | 0 | 10/12 | 4.17 |

**all labels** (TP/FP/FN/TN = confusion matrix; P and R with Wilson 95% interval)

| Label | System | Pos | TP | FP | FN | TN | Precision | Recall | F1 |
|---|---|---|---|---|---|---|---|---|---|
| mentioned | baseline | 11 | 11 | 0 | 0 | 1 | 1.0 [0.74, 1.0] | 1.0 [0.74, 1.0] | 1.0 |
| mentioned | classify-v1 | 11 | 11 | 0 | 0 | 1 | 1.0 [0.74, 1.0] | 1.0 [0.74, 1.0] | 1.0 |
| mentioned | classify-v2 | 11 | 11 | 0 | 0 | 1 | 1.0 [0.74, 1.0] | 1.0 [0.74, 1.0] | 1.0 |
| recommended | baseline | 1 | 0 | 2 | 1 | 9 | 0.0 [0.0, 0.66] | 0.0 [0.0, 0.79] | 0.0 |
| recommended | classify-v1 | 1 | 1 | 3 | 0 | 8 | 0.25 [0.05, 0.7] | 1.0 [0.21, 1.0] | 0.4 |
| recommended | classify-v2 | 1 | 1 | 0 | 0 | 11 | 1.0 [0.21, 1.0] | 1.0 [0.21, 1.0] | 1.0 |
| negative | baseline | 2 | 1 | 3 | 1 | 7 | 0.25 [0.05, 0.7] | 0.5 [0.09, 0.91] | 0.333 |
| negative | classify-v1 | 2 | 2 | 3 | 0 | 7 | 0.4 [0.12, 0.77] | 1.0 [0.34, 1.0] | 0.571 |
| negative | classify-v2 | 2 | 2 | 2 | 0 | 8 | 0.5 [0.15, 0.85] | 1.0 [0.34, 1.0] | 0.667 |
| entity_confusion | baseline | 3 | 3 | 1 | 0 | 8 | 0.75 [0.3, 0.95] | 1.0 [0.44, 1.0] | 0.857 |
| entity_confusion | classify-v1 | 3 | 3 | 0 | 0 | 9 | 1.0 [0.44, 1.0] | 1.0 [0.44, 1.0] | 1.0 |
| entity_confusion | classify-v2 | 3 | 3 | 0 | 0 | 9 | 1.0 [0.44, 1.0] | 1.0 [0.44, 1.0] | 1.0 |

**ambiguous labels excluded** (TP/FP/FN/TN = confusion matrix; P and R with Wilson 95% interval)

| Label | System | Pos | TP | FP | FN | TN | Precision | Recall | F1 |
|---|---|---|---|---|---|---|---|---|---|
| mentioned | baseline | 11 | 11 | 0 | 0 | 1 | 1.0 [0.74, 1.0] | 1.0 [0.74, 1.0] | 1.0 |
| mentioned | classify-v1 | 11 | 11 | 0 | 0 | 1 | 1.0 [0.74, 1.0] | 1.0 [0.74, 1.0] | 1.0 |
| mentioned | classify-v2 | 11 | 11 | 0 | 0 | 1 | 1.0 [0.74, 1.0] | 1.0 [0.74, 1.0] | 1.0 |
| recommended | baseline | 0 | 0 | 2 | 0 | 9 | 0.0 [0.0, 0.66] | n/a | 0.0 |
| recommended | classify-v1 | 0 | 0 | 3 | 0 | 8 | 0.0 [0.0, 0.56] | n/a | 0.0 |
| recommended | classify-v2 | 0 | 0 | 0 | 0 | 11 | n/a | n/a | n/a |
| negative | baseline | 2 | 1 | 1 | 1 | 7 | 0.5 [0.09, 0.91] | 0.5 [0.09, 0.91] | 0.5 |
| negative | classify-v1 | 2 | 2 | 1 | 0 | 7 | 0.667 [0.21, 0.94] | 1.0 [0.34, 1.0] | 0.8 |
| negative | classify-v2 | 2 | 2 | 0 | 0 | 8 | 1.0 [0.34, 1.0] | 1.0 [0.34, 1.0] | 1.0 |
| entity_confusion | baseline | 3 | 3 | 1 | 0 | 8 | 0.75 [0.3, 0.95] | 1.0 [0.44, 1.0] | 0.857 |
| entity_confusion | classify-v1 | 3 | 3 | 0 | 0 | 9 | 1.0 [0.44, 1.0] | 1.0 [0.44, 1.0] | 1.0 |
| entity_confusion | classify-v2 | 3 | 3 | 0 | 0 | 9 | 1.0 [0.44, 1.0] | 1.0 [0.44, 1.0] | 1.0 |

**Errors by case (strict)**

| Label | System | False positives | False negatives |
|---|---|---|---|
| recommended | baseline | D-010-chatgpt, D-017-chatgpt | D-017-aimode |
| recommended | classify-v1 | D-004-gemini, D-010-gemini, D-017-gemini | - |
| negative | baseline | D-010-chatgpt, D-010-gemini, D-025-chatgpt | D-017-chatgpt |
| negative | classify-v1 | D-004-aimode, D-010-chatgpt, D-025-chatgpt | - |
| negative | classify-v2 | D-010-chatgpt, D-025-chatgpt | - |
| entity_confusion | baseline | D-017-chatgpt | - |

classify-v2 recommendation_type distribution: {'neutral_description': 7, 'factual_answer': 2, 'suitability_claim': 1, 'negative_or_alternative': 1, 'not_applicable': 1}

## final_seen (14 cases)

| System | Succeeded | Failed | Score exact | Score MAE |
|---|---|---|---|---|
| baseline | 14 | 0 | 9/14 | 12.14 |
| classify-v1 | 14 | 0 | 8/14 | 17.14 |
| classify-v2 | 14 | 0 | 12/14 | 2.86 |

**all labels** (TP/FP/FN/TN = confusion matrix; P and R with Wilson 95% interval)

| Label | System | Pos | TP | FP | FN | TN | Precision | Recall | F1 |
|---|---|---|---|---|---|---|---|---|---|
| mentioned | baseline | 11 | 11 | 0 | 0 | 3 | 1.0 [0.74, 1.0] | 1.0 [0.74, 1.0] | 1.0 |
| mentioned | classify-v1 | 11 | 11 | 0 | 0 | 3 | 1.0 [0.74, 1.0] | 1.0 [0.74, 1.0] | 1.0 |
| mentioned | classify-v2 | 11 | 11 | 0 | 0 | 3 | 1.0 [0.74, 1.0] | 1.0 [0.74, 1.0] | 1.0 |
| recommended | baseline | 2 | 2 | 1 | 0 | 11 | 0.667 [0.21, 0.94] | 1.0 [0.34, 1.0] | 0.8 |
| recommended | classify-v1 | 2 | 2 | 5 | 0 | 7 | 0.286 [0.08, 0.64] | 1.0 [0.34, 1.0] | 0.444 |
| recommended | classify-v2 | 2 | 2 | 0 | 0 | 12 | 1.0 [0.34, 1.0] | 1.0 [0.34, 1.0] | 1.0 |
| negative | baseline | 4 | 1 | 0 | 3 | 10 | 1.0 [0.21, 1.0] | 0.25 [0.05, 0.7] | 0.4 |
| negative | classify-v1 | 4 | 4 | 1 | 0 | 9 | 0.8 [0.38, 0.96] | 1.0 [0.51, 1.0] | 0.889 |
| negative | classify-v2 | 4 | 4 | 1 | 0 | 9 | 0.8 [0.38, 0.96] | 1.0 [0.51, 1.0] | 0.889 |
| entity_confusion | baseline | 3 | 1 | 0 | 2 | 11 | 1.0 [0.21, 1.0] | 0.333 [0.06, 0.79] | 0.5 |
| entity_confusion | classify-v1 | 3 | 2 | 0 | 1 | 11 | 1.0 [0.34, 1.0] | 0.667 [0.21, 0.94] | 0.8 |
| entity_confusion | classify-v2 | 3 | 2 | 0 | 1 | 11 | 1.0 [0.34, 1.0] | 0.667 [0.21, 0.94] | 0.8 |

**ambiguous labels excluded** (TP/FP/FN/TN = confusion matrix; P and R with Wilson 95% interval)

| Label | System | Pos | TP | FP | FN | TN | Precision | Recall | F1 |
|---|---|---|---|---|---|---|---|---|---|
| mentioned | baseline | 11 | 11 | 0 | 0 | 3 | 1.0 [0.74, 1.0] | 1.0 [0.74, 1.0] | 1.0 |
| mentioned | classify-v1 | 11 | 11 | 0 | 0 | 3 | 1.0 [0.74, 1.0] | 1.0 [0.74, 1.0] | 1.0 |
| mentioned | classify-v2 | 11 | 11 | 0 | 0 | 3 | 1.0 [0.74, 1.0] | 1.0 [0.74, 1.0] | 1.0 |
| recommended | baseline | 2 | 2 | 1 | 0 | 8 | 0.667 [0.21, 0.94] | 1.0 [0.34, 1.0] | 0.8 |
| recommended | classify-v1 | 2 | 2 | 2 | 0 | 7 | 0.5 [0.15, 0.85] | 1.0 [0.34, 1.0] | 0.667 |
| recommended | classify-v2 | 2 | 2 | 0 | 0 | 9 | 1.0 [0.34, 1.0] | 1.0 [0.34, 1.0] | 1.0 |
| negative | baseline | 2 | 0 | 0 | 2 | 9 | n/a | 0.0 [0.0, 0.66] | 0.0 |
| negative | classify-v1 | 2 | 2 | 0 | 0 | 9 | 1.0 [0.34, 1.0] | 1.0 [0.34, 1.0] | 1.0 |
| negative | classify-v2 | 2 | 2 | 0 | 0 | 9 | 1.0 [0.34, 1.0] | 1.0 [0.34, 1.0] | 1.0 |
| entity_confusion | baseline | 3 | 1 | 0 | 2 | 11 | 1.0 [0.21, 1.0] | 0.333 [0.06, 0.79] | 0.5 |
| entity_confusion | classify-v1 | 3 | 2 | 0 | 1 | 11 | 1.0 [0.34, 1.0] | 0.667 [0.21, 0.94] | 0.8 |
| entity_confusion | classify-v2 | 3 | 2 | 0 | 1 | 11 | 1.0 [0.34, 1.0] | 0.667 [0.21, 0.94] | 0.8 |

**Errors by case (strict)**

| Label | System | False positives | False negatives |
|---|---|---|---|
| recommended | baseline | S02 | - |
| recommended | classify-v1 | H05, H06, H07, H10, H11 | - |
| negative | baseline | - | H02, H07, S02 |
| negative | classify-v1 | H01 | - |
| negative | classify-v2 | H01 | - |
| entity_confusion | baseline | - | H01, H06 |
| entity_confusion | classify-v1 | - | H06 |
| entity_confusion | classify-v2 | - | H06 |

classify-v2 recommendation_type distribution: {'neutral_description': 5, 'negative_or_alternative': 1, 'not_applicable': 3, 'factual_answer': 3, 'suitability_claim': 1, 'explicit_endorsement': 1}

## holdout2 (24 cases)

| System | Succeeded | Failed | Score exact | Score MAE |
|---|---|---|---|---|
| baseline | 24 | 0 | 13/24 | 15.0 |
| classify-v1 | 23 | 1 | 7/23 | 20.0 |
| classify-v2 | 24 | 0 | 15/24 | 10.83 |

**all labels** (TP/FP/FN/TN = confusion matrix; P and R with Wilson 95% interval)

| Label | System | Pos | TP | FP | FN | TN | Precision | Recall | F1 |
|---|---|---|---|---|---|---|---|---|---|
| mentioned | baseline | 24 | 24 | 0 | 0 | 0 | 1.0 [0.86, 1.0] | 1.0 [0.86, 1.0] | 1.0 |
| mentioned | classify-v1 | 23 | 23 | 0 | 0 | 0 | 1.0 [0.86, 1.0] | 1.0 [0.86, 1.0] | 1.0 |
| mentioned | classify-v2 | 24 | 24 | 0 | 0 | 0 | 1.0 [0.86, 1.0] | 1.0 [0.86, 1.0] | 1.0 |
| recommended | baseline | 1 | 0 | 4 | 1 | 19 | 0.0 [0.0, 0.49] | 0.0 [0.0, 0.79] | 0.0 |
| recommended | classify-v1 | 1 | 1 | 10 | 0 | 12 | 0.091 [0.02, 0.38] | 1.0 [0.21, 1.0] | 0.167 |
| recommended | classify-v2 | 1 | 1 | 2 | 0 | 21 | 0.333 [0.06, 0.79] | 1.0 [0.21, 1.0] | 0.5 |
| negative | baseline | 4 | 3 | 5 | 1 | 15 | 0.375 [0.14, 0.69] | 0.75 [0.3, 0.95] | 0.5 |
| negative | classify-v1 | 4 | 4 | 6 | 0 | 13 | 0.4 [0.17, 0.69] | 1.0 [0.51, 1.0] | 0.571 |
| negative | classify-v2 | 4 | 3 | 3 | 1 | 17 | 0.5 [0.19, 0.81] | 0.75 [0.3, 0.95] | 0.6 |
| entity_confusion | baseline | 4 | 2 | 0 | 2 | 20 | 1.0 [0.34, 1.0] | 0.5 [0.15, 0.85] | 0.667 |
| entity_confusion | classify-v1 | 4 | 0 | 0 | 4 | 19 | n/a | 0.0 [0.0, 0.49] | 0.0 |
| entity_confusion | classify-v2 | 4 | 1 | 0 | 3 | 20 | 1.0 [0.21, 1.0] | 0.25 [0.05, 0.7] | 0.4 |

**ambiguous labels excluded** (TP/FP/FN/TN = confusion matrix; P and R with Wilson 95% interval)

| Label | System | Pos | TP | FP | FN | TN | Precision | Recall | F1 |
|---|---|---|---|---|---|---|---|---|---|
| mentioned | baseline | 24 | 24 | 0 | 0 | 0 | 1.0 [0.86, 1.0] | 1.0 [0.86, 1.0] | 1.0 |
| mentioned | classify-v1 | 23 | 23 | 0 | 0 | 0 | 1.0 [0.86, 1.0] | 1.0 [0.86, 1.0] | 1.0 |
| mentioned | classify-v2 | 24 | 24 | 0 | 0 | 0 | 1.0 [0.86, 1.0] | 1.0 [0.86, 1.0] | 1.0 |
| recommended | baseline | 0 | 0 | 3 | 0 | 19 | 0.0 [0.0, 0.56] | n/a | 0.0 |
| recommended | classify-v1 | 0 | 0 | 9 | 0 | 12 | 0.0 [0.0, 0.3] | n/a | 0.0 |
| recommended | classify-v2 | 0 | 0 | 1 | 0 | 21 | 0.0 [0.0, 0.79] | n/a | 0.0 |
| negative | baseline | 0 | 0 | 4 | 0 | 13 | 0.0 [0.0, 0.49] | n/a | 0.0 |
| negative | classify-v1 | 0 | 0 | 5 | 0 | 12 | 0.0 [-0.0, 0.43] | n/a | 0.0 |
| negative | classify-v2 | 0 | 0 | 1 | 0 | 16 | 0.0 [0.0, 0.79] | n/a | 0.0 |
| entity_confusion | baseline | 2 | 2 | 0 | 0 | 19 | 1.0 [0.34, 1.0] | 1.0 [0.34, 1.0] | 1.0 |
| entity_confusion | classify-v1 | 2 | 0 | 0 | 2 | 18 | n/a | 0.0 [0.0, 0.66] | 0.0 |
| entity_confusion | classify-v2 | 2 | 1 | 0 | 1 | 19 | 1.0 [0.21, 1.0] | 0.5 [0.09, 0.91] | 0.667 |

**Errors by case (strict)**

| Label | System | False positives | False negatives |
|---|---|---|---|
| recommended | baseline | H2-006-gemini, H2-012-aimode, H2-020-gemini, H2-021-aimode | H2-008-chatgpt |
| recommended | classify-v1 | H2-005-aimode, H2-005-chatgpt, H2-005-gemini, H2-006-chatgpt, H2-006-gemini, H2-018-gemini, H2-019-gemini, H2-020-aimode, H2-020-gemini, H2-021-aimode | - |
| recommended | classify-v2 | H2-006-gemini, H2-021-aimode | - |
| negative | baseline | H2-018-chatgpt, H2-019-aimode, H2-019-chatgpt, H2-020-chatgpt, H2-021-chatgpt | H2-012-aimode |
| negative | classify-v1 | H2-005-aimode, H2-005-gemini, H2-008-aimode, H2-018-chatgpt, H2-019-chatgpt, H2-021-chatgpt | - |
| negative | classify-v2 | H2-005-aimode, H2-012-gemini, H2-021-chatgpt | H2-006-chatgpt |
| entity_confusion | baseline | - | H2-006-aimode, H2-019-aimode |
| entity_confusion | classify-v1 | - | H2-006-aimode, H2-018-chatgpt, H2-019-aimode, H2-019-chatgpt |
| entity_confusion | classify-v2 | - | H2-006-aimode, H2-019-aimode, H2-019-chatgpt |

**Failed analyses:** H2-012-gemini: invalid_output: mentioned: quote not found in answer: 'Kasparro builds an AI Visibility platform' (after 3 attempts)

classify-v2 recommendation_type distribution: {'neutral_description': 15, 'factual_answer': 5, 'suitability_claim': 2, 'explicit_endorsement': 1, 'not_applicable': 1}

## synthetic_robust (10 cases)

| System | Succeeded | Failed | Score exact | Score MAE |
|---|---|---|---|---|
| baseline | 10 | 0 | 6/10 | 13.0 |
| classify-v1 | 10 | 0 | 6/10 | 16.0 |
| classify-v2 | 9 | 1 | 9/9 | 0.0 |

**all labels** (TP/FP/FN/TN = confusion matrix; P and R with Wilson 95% interval)

| Label | System | Pos | TP | FP | FN | TN | Precision | Recall | F1 |
|---|---|---|---|---|---|---|---|---|---|
| mentioned | baseline | 9 | 9 | 0 | 0 | 1 | 1.0 [0.7, 1.0] | 1.0 [0.7, 1.0] | 1.0 |
| mentioned | classify-v1 | 9 | 9 | 0 | 0 | 1 | 1.0 [0.7, 1.0] | 1.0 [0.7, 1.0] | 1.0 |
| mentioned | classify-v2 | 8 | 8 | 0 | 0 | 1 | 1.0 [0.68, 1.0] | 1.0 [0.68, 1.0] | 1.0 |
| recommended | baseline | 2 | 1 | 0 | 1 | 8 | 1.0 [0.21, 1.0] | 0.5 [0.09, 0.91] | 0.667 |
| recommended | classify-v1 | 2 | 2 | 4 | 0 | 4 | 0.333 [0.1, 0.7] | 1.0 [0.34, 1.0] | 0.5 |
| recommended | classify-v2 | 2 | 2 | 0 | 0 | 7 | 1.0 [0.34, 1.0] | 1.0 [0.34, 1.0] | 1.0 |
| negative | baseline | 4 | 1 | 0 | 3 | 6 | 1.0 [0.21, 1.0] | 0.25 [0.05, 0.7] | 0.4 |
| negative | classify-v1 | 4 | 4 | 0 | 0 | 6 | 1.0 [0.51, 1.0] | 1.0 [0.51, 1.0] | 1.0 |
| negative | classify-v2 | 3 | 3 | 0 | 0 | 6 | 1.0 [0.44, 1.0] | 1.0 [0.44, 1.0] | 1.0 |
| entity_confusion | baseline | 1 | 1 | 0 | 0 | 9 | 1.0 [0.21, 1.0] | 1.0 [0.21, 1.0] | 1.0 |
| entity_confusion | classify-v1 | 1 | 1 | 0 | 0 | 9 | 1.0 [0.21, 1.0] | 1.0 [0.21, 1.0] | 1.0 |
| entity_confusion | classify-v2 | 1 | 1 | 0 | 0 | 8 | 1.0 [0.21, 1.0] | 1.0 [0.21, 1.0] | 1.0 |

**ambiguous labels excluded** (TP/FP/FN/TN = confusion matrix; P and R with Wilson 95% interval)

| Label | System | Pos | TP | FP | FN | TN | Precision | Recall | F1 |
|---|---|---|---|---|---|---|---|---|---|
| mentioned | baseline | 9 | 9 | 0 | 0 | 1 | 1.0 [0.7, 1.0] | 1.0 [0.7, 1.0] | 1.0 |
| mentioned | classify-v1 | 9 | 9 | 0 | 0 | 1 | 1.0 [0.7, 1.0] | 1.0 [0.7, 1.0] | 1.0 |
| mentioned | classify-v2 | 8 | 8 | 0 | 0 | 1 | 1.0 [0.68, 1.0] | 1.0 [0.68, 1.0] | 1.0 |
| recommended | baseline | 2 | 1 | 0 | 1 | 8 | 1.0 [0.21, 1.0] | 0.5 [0.09, 0.91] | 0.667 |
| recommended | classify-v1 | 2 | 2 | 4 | 0 | 4 | 0.333 [0.1, 0.7] | 1.0 [0.34, 1.0] | 0.5 |
| recommended | classify-v2 | 2 | 2 | 0 | 0 | 7 | 1.0 [0.34, 1.0] | 1.0 [0.34, 1.0] | 1.0 |
| negative | baseline | 3 | 1 | 0 | 2 | 6 | 1.0 [0.21, 1.0] | 0.333 [0.06, 0.79] | 0.5 |
| negative | classify-v1 | 3 | 3 | 0 | 0 | 6 | 1.0 [0.44, 1.0] | 1.0 [0.44, 1.0] | 1.0 |
| negative | classify-v2 | 3 | 3 | 0 | 0 | 6 | 1.0 [0.44, 1.0] | 1.0 [0.44, 1.0] | 1.0 |
| entity_confusion | baseline | 1 | 1 | 0 | 0 | 9 | 1.0 [0.21, 1.0] | 1.0 [0.21, 1.0] | 1.0 |
| entity_confusion | classify-v1 | 1 | 1 | 0 | 0 | 9 | 1.0 [0.21, 1.0] | 1.0 [0.21, 1.0] | 1.0 |
| entity_confusion | classify-v2 | 1 | 1 | 0 | 0 | 8 | 1.0 [0.21, 1.0] | 1.0 [0.21, 1.0] | 1.0 |

**Errors by case (strict)**

| Label | System | False positives | False negatives |
|---|---|---|---|
| recommended | baseline | - | SR01 |
| recommended | classify-v1 | SR02, SR03, SR08, SR10 | - |
| negative | baseline | - | SR05, SR06, SR08 |

**Failed analyses:** SR08: invalid_output: recommended is true but no evidence quote was given (after 3 attempts)

classify-v2 recommendation_type distribution: {'explicit_endorsement': 1, 'neutral_description': 2, 'factual_answer': 1, 'negative_or_alternative': 3, 'not_applicable': 1, 'None': 1, 'suitability_claim': 1}

## Provenance

```
{
 "generated_at": "2026-10-29T09:07:23+00:00",
 "fresh": "fresh-v2",
 "label_files": {
  "labels_v3.jsonl": "a893038eb00bd4c7",
  "fresh_v2.jsonl": "e5efcf2ddc070908"
 },
 "providers": {
  "classify-v1": "replay",
  "classify-v2": "replay"
 },
 "model": "replay:gemma4:12b",
 "baseline": "baseline-v1",
 "prompt_files": {
  "classify-v1": "c339efedb0594aad",
  "classify-v2": "3d726ce8e959b1d2"
 },
 "splits_run": [
  "tuning",
  "dev",
  "final_seen",
  "holdout2",
  "synthetic_robust"
 ]
}
```
