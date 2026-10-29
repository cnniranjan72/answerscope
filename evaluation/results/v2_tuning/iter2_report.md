# Comparison report: baseline vs classify-v1 vs classify-v2

Generated 2026-10-29T03:20:42+00:00 | labels {'labels_v3.jsonl': 'a893038eb00bd4c7', 'fresh_v1.jsonl': 'c144389e44447789'} | score `vis-v1` | v1 `replay` | v2 `local_model`

> **Read holdout2 for independent evidence.** final_seen was inspected while designing classify-v2; dev was used to tune it. Labels: labels-v3 (candidate-reviewed) and fresh-v1 (AI-drafted, blind to predictions, candidate review pending). Intervals are Wilson 95% on tiny counts: treat them as a warning about uncertainty, not as significance tests.

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
| baseline | 12 | 0 | 8/12 | 9.17 |
| classify-v1 | 12 | 0 | 5/12 | 20.0 |
| classify-v2 | 12 | 0 | 8/12 | 10.83 |

**all labels** (TP/FP/FN/TN = confusion matrix; P and R with Wilson 95% interval)

| Label | System | Pos | TP | FP | FN | TN | Precision | Recall | F1 |
|---|---|---|---|---|---|---|---|---|---|
| mentioned | baseline | 11 | 11 | 0 | 0 | 1 | 1.0 [0.74, 1.0] | 1.0 [0.74, 1.0] | 1.0 |
| mentioned | classify-v1 | 11 | 11 | 0 | 0 | 1 | 1.0 [0.74, 1.0] | 1.0 [0.74, 1.0] | 1.0 |
| mentioned | classify-v2 | 11 | 11 | 0 | 0 | 1 | 1.0 [0.74, 1.0] | 1.0 [0.74, 1.0] | 1.0 |
| recommended | baseline | 0 | 0 | 2 | 0 | 10 | 0.0 [0.0, 0.66] | n/a | 0.0 |
| recommended | classify-v1 | 0 | 0 | 4 | 0 | 8 | 0.0 [0.0, 0.49] | n/a | 0.0 |
| recommended | classify-v2 | 0 | 0 | 2 | 0 | 10 | 0.0 [0.0, 0.66] | n/a | 0.0 |
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
| recommended | classify-v2 | 0 | 0 | 1 | 0 | 10 | 0.0 [0.0, 0.79] | n/a | 0.0 |
| negative | baseline | 2 | 1 | 1 | 1 | 7 | 0.5 [0.09, 0.91] | 0.5 [0.09, 0.91] | 0.5 |
| negative | classify-v1 | 2 | 2 | 1 | 0 | 7 | 0.667 [0.21, 0.94] | 1.0 [0.34, 1.0] | 0.8 |
| negative | classify-v2 | 2 | 2 | 0 | 0 | 8 | 1.0 [0.34, 1.0] | 1.0 [0.34, 1.0] | 1.0 |
| entity_confusion | baseline | 3 | 3 | 1 | 0 | 8 | 0.75 [0.3, 0.95] | 1.0 [0.44, 1.0] | 0.857 |
| entity_confusion | classify-v1 | 3 | 3 | 0 | 0 | 9 | 1.0 [0.44, 1.0] | 1.0 [0.44, 1.0] | 1.0 |
| entity_confusion | classify-v2 | 3 | 3 | 0 | 0 | 9 | 1.0 [0.44, 1.0] | 1.0 [0.44, 1.0] | 1.0 |

**Errors by case (strict)**

| Label | System | False positives | False negatives |
|---|---|---|---|
| recommended | baseline | D-010-chatgpt, D-017-chatgpt | - |
| recommended | classify-v1 | D-004-gemini, D-010-gemini, D-017-aimode, D-017-gemini | - |
| recommended | classify-v2 | D-017-aimode, D-017-gemini | - |
| negative | baseline | D-010-chatgpt, D-010-gemini, D-025-chatgpt | D-017-chatgpt |
| negative | classify-v1 | D-004-aimode, D-010-chatgpt, D-025-chatgpt | - |
| negative | classify-v2 | D-010-chatgpt, D-025-chatgpt | - |
| entity_confusion | baseline | D-017-chatgpt | - |

classify-v2 recommendation_type distribution: {'neutral_description': 5, 'factual_answer': 3, 'suitability_claim': 2, 'negative_or_alternative': 1, 'not_applicable': 1}

## final_seen (0 cases)

| System | Succeeded | Failed | Score exact | Score MAE |
|---|---|---|---|---|
| baseline | 0 | 0 | 0/0 | None |
| classify-v1 | 0 | 0 | 0/0 | None |
| classify-v2 | 0 | 0 | 0/0 | None |

**all labels** (TP/FP/FN/TN = confusion matrix; P and R with Wilson 95% interval)

| Label | System | Pos | TP | FP | FN | TN | Precision | Recall | F1 |
|---|---|---|---|---|---|---|---|---|---|
| mentioned | baseline | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| mentioned | classify-v1 | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| mentioned | classify-v2 | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| recommended | baseline | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| recommended | classify-v1 | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| recommended | classify-v2 | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| negative | baseline | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| negative | classify-v1 | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| negative | classify-v2 | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| entity_confusion | baseline | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| entity_confusion | classify-v1 | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| entity_confusion | classify-v2 | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |

**ambiguous labels excluded** (TP/FP/FN/TN = confusion matrix; P and R with Wilson 95% interval)

| Label | System | Pos | TP | FP | FN | TN | Precision | Recall | F1 |
|---|---|---|---|---|---|---|---|---|---|
| mentioned | baseline | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| mentioned | classify-v1 | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| mentioned | classify-v2 | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| recommended | baseline | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| recommended | classify-v1 | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| recommended | classify-v2 | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| negative | baseline | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| negative | classify-v1 | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| negative | classify-v2 | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| entity_confusion | baseline | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| entity_confusion | classify-v1 | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| entity_confusion | classify-v2 | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |

**Errors by case (strict)**

| Label | System | False positives | False negatives |
|---|---|---|---|

classify-v2 recommendation_type distribution: {}

## holdout2 (0 cases)

| System | Succeeded | Failed | Score exact | Score MAE |
|---|---|---|---|---|
| baseline | 0 | 0 | 0/0 | None |
| classify-v1 | 0 | 0 | 0/0 | None |
| classify-v2 | 0 | 0 | 0/0 | None |

**all labels** (TP/FP/FN/TN = confusion matrix; P and R with Wilson 95% interval)

| Label | System | Pos | TP | FP | FN | TN | Precision | Recall | F1 |
|---|---|---|---|---|---|---|---|---|---|
| mentioned | baseline | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| mentioned | classify-v1 | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| mentioned | classify-v2 | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| recommended | baseline | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| recommended | classify-v1 | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| recommended | classify-v2 | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| negative | baseline | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| negative | classify-v1 | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| negative | classify-v2 | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| entity_confusion | baseline | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| entity_confusion | classify-v1 | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| entity_confusion | classify-v2 | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |

**ambiguous labels excluded** (TP/FP/FN/TN = confusion matrix; P and R with Wilson 95% interval)

| Label | System | Pos | TP | FP | FN | TN | Precision | Recall | F1 |
|---|---|---|---|---|---|---|---|---|---|
| mentioned | baseline | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| mentioned | classify-v1 | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| mentioned | classify-v2 | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| recommended | baseline | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| recommended | classify-v1 | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| recommended | classify-v2 | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| negative | baseline | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| negative | classify-v1 | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| negative | classify-v2 | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| entity_confusion | baseline | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| entity_confusion | classify-v1 | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| entity_confusion | classify-v2 | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |

**Errors by case (strict)**

| Label | System | False positives | False negatives |
|---|---|---|---|

classify-v2 recommendation_type distribution: {}

## synthetic_robust (0 cases)

| System | Succeeded | Failed | Score exact | Score MAE |
|---|---|---|---|---|
| baseline | 0 | 0 | 0/0 | None |
| classify-v1 | 0 | 0 | 0/0 | None |
| classify-v2 | 0 | 0 | 0/0 | None |

**all labels** (TP/FP/FN/TN = confusion matrix; P and R with Wilson 95% interval)

| Label | System | Pos | TP | FP | FN | TN | Precision | Recall | F1 |
|---|---|---|---|---|---|---|---|---|---|
| mentioned | baseline | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| mentioned | classify-v1 | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| mentioned | classify-v2 | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| recommended | baseline | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| recommended | classify-v1 | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| recommended | classify-v2 | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| negative | baseline | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| negative | classify-v1 | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| negative | classify-v2 | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| entity_confusion | baseline | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| entity_confusion | classify-v1 | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| entity_confusion | classify-v2 | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |

**ambiguous labels excluded** (TP/FP/FN/TN = confusion matrix; P and R with Wilson 95% interval)

| Label | System | Pos | TP | FP | FN | TN | Precision | Recall | F1 |
|---|---|---|---|---|---|---|---|---|---|
| mentioned | baseline | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| mentioned | classify-v1 | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| mentioned | classify-v2 | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| recommended | baseline | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| recommended | classify-v1 | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| recommended | classify-v2 | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| negative | baseline | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| negative | classify-v1 | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| negative | classify-v2 | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| entity_confusion | baseline | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| entity_confusion | classify-v1 | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |
| entity_confusion | classify-v2 | 0 | 0 | 0 | 0 | 0 | n/a | n/a | n/a |

**Errors by case (strict)**

| Label | System | False positives | False negatives |
|---|---|---|---|

classify-v2 recommendation_type distribution: {}

## Provenance

```
{
 "generated_at": "2026-10-29T03:20:42+00:00",
 "label_files": {
  "labels_v3.jsonl": "a893038eb00bd4c7",
  "fresh_v1.jsonl": "c144389e44447789"
 },
 "providers": {
  "classify-v1": "replay",
  "classify-v2": "local_model"
 },
 "model": "gemma4:12b",
 "baseline": "baseline-v1",
 "prompt_files": {
  "classify-v1": "c339efedb0594aad",
  "classify-v2": "98c5338902db2c9e"
 },
 "splits_run": [
  "tuning",
  "dev"
 ]
}
```
