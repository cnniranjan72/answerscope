# Evaluation report

Generated 2026-10-29T01:59:57+00:00 | labels `labels-v3` | prompt `classify-v1` | score `vis-v1` | baseline `baseline-v1`

**Model system:** provider `replay`, execution mode `replay`, model `replay:gemma4:12b`.

> Replay mode: recorded outputs from one earlier local-model run are re-validated by current code. This reproduces that run; it does not measure run-to-run variance.

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
| recommended | model | 2 | 2 | 5 | 0 | 7 | 0.29 | 1.00 | 0.44 | 0.64 |
| negative | baseline | 4 | 1 | 0 | 3 | 10 | 1.00 | 0.25 | 0.40 | 0.79 |
| negative | model | 4 | 4 | 1 | 0 | 9 | 0.80 | 1.00 | 0.89 | 0.93 |
| entity_confusion | baseline | 3 | 1 | 0 | 2 | 11 | 1.00 | 0.33 | 0.50 | 0.86 |
| entity_confusion | model | 3 | 2 | 0 | 1 | 11 | 1.00 | 0.67 | 0.80 | 0.93 |

**Per-label metrics (ambiguous labels excluded)**

| Label | System | Positives | TP | FP | FN | TN | Precision | Recall | F1 | Agreement |
|---|---|---|---|---|---|---|---|---|---|---|
| mentioned | baseline | 11 | 11 | 0 | 0 | 3 | 1.00 | 1.00 | 1.00 | 1.00 |
| mentioned | model | 11 | 11 | 0 | 0 | 3 | 1.00 | 1.00 | 1.00 | 1.00 |
| recommended | baseline | 2 | 2 | 1 | 0 | 8 | 0.67 | 1.00 | 0.80 | 0.91 |
| recommended | model | 2 | 2 | 2 | 0 | 7 | 0.50 | 1.00 | 0.67 | 0.82 |
| negative | baseline | 2 | 0 | 0 | 2 | 9 | n/a | 0.00 | 0.00 | 0.82 |
| negative | model | 2 | 2 | 0 | 0 | 9 | 1.00 | 1.00 | 1.00 | 1.00 |
| entity_confusion | baseline | 3 | 1 | 0 | 2 | 11 | 1.00 | 0.33 | 0.50 | 0.86 |
| entity_confusion | model | 3 | 2 | 0 | 1 | 11 | 1.00 | 0.67 | 0.80 | 0.93 |

| System | Competitor precision | Competitor recall | Score exact | Score MAE | Position exact |
|---|---|---|---|---|---|
| baseline | 1.00 (tp 14, fp 0) | 0.88 (fn 2) | 9/14 | 12.14 | 0/1 |
| model | 0.94 (tp 16, fp 1) | 1.00 (fn 0) | 8/14 | 17.14 | 1/1 |

## Final_Sensitivity split (13 cases: H01, H02, H03, H04, H05, H06, H07, H08, H09, H10, H12, S01, S02)

| System | Eligible | Succeeded | Failed | Skipped |
|---|---|---|---|---|
| baseline | 13 | 13 | 0 | 0 |
| model | 13 | 13 | 0 | 0 |

**Per-label metrics (all labels)**

| Label | System | Positives | TP | FP | FN | TN | Precision | Recall | F1 | Agreement |
|---|---|---|---|---|---|---|---|---|---|---|
| mentioned | baseline | 10 | 10 | 0 | 0 | 3 | 1.00 | 1.00 | 1.00 | 1.00 |
| mentioned | model | 10 | 10 | 0 | 0 | 3 | 1.00 | 1.00 | 1.00 | 1.00 |
| recommended | baseline | 2 | 2 | 1 | 0 | 10 | 0.67 | 1.00 | 0.80 | 0.92 |
| recommended | model | 2 | 2 | 4 | 0 | 7 | 0.33 | 1.00 | 0.50 | 0.69 |
| negative | baseline | 4 | 1 | 0 | 3 | 9 | 1.00 | 0.25 | 0.40 | 0.77 |
| negative | model | 4 | 4 | 1 | 0 | 8 | 0.80 | 1.00 | 0.89 | 0.92 |
| entity_confusion | baseline | 3 | 1 | 0 | 2 | 10 | 1.00 | 0.33 | 0.50 | 0.85 |
| entity_confusion | model | 3 | 2 | 0 | 1 | 10 | 1.00 | 0.67 | 0.80 | 0.92 |

**Per-label metrics (ambiguous labels excluded)**

| Label | System | Positives | TP | FP | FN | TN | Precision | Recall | F1 | Agreement |
|---|---|---|---|---|---|---|---|---|---|---|
| mentioned | baseline | 10 | 10 | 0 | 0 | 3 | 1.00 | 1.00 | 1.00 | 1.00 |
| mentioned | model | 10 | 10 | 0 | 0 | 3 | 1.00 | 1.00 | 1.00 | 1.00 |
| recommended | baseline | 2 | 2 | 1 | 0 | 7 | 0.67 | 1.00 | 0.80 | 0.90 |
| recommended | model | 2 | 2 | 1 | 0 | 7 | 0.67 | 1.00 | 0.80 | 0.90 |
| negative | baseline | 2 | 0 | 0 | 2 | 8 | n/a | 0.00 | 0.00 | 0.80 |
| negative | model | 2 | 2 | 0 | 0 | 8 | 1.00 | 1.00 | 1.00 | 1.00 |
| entity_confusion | baseline | 3 | 1 | 0 | 2 | 10 | 1.00 | 0.33 | 0.50 | 0.85 |
| entity_confusion | model | 3 | 2 | 0 | 1 | 10 | 1.00 | 0.67 | 0.80 | 0.92 |

| System | Competitor precision | Competitor recall | Score exact | Score MAE | Position exact |
|---|---|---|---|---|---|
| baseline | 1.00 (tp 14, fp 0) | 0.88 (fn 2) | 8/13 | 13.08 | 0/1 |
| model | 0.94 (tp 16, fp 1) | 1.00 (fn 0) | 8/13 | 15.38 | 1/1 |

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
| negative | baseline | 1 | 1 | 0 | 0 | 3 | 1.00 | 1.00 | 1.00 | 1.00 |
| negative | model | 1 | 1 | 0 | 0 | 3 | 1.00 | 1.00 | 1.00 | 1.00 |
| entity_confusion | baseline | 1 | 1 | 0 | 0 | 4 | 1.00 | 1.00 | 1.00 | 1.00 |
| entity_confusion | model | 1 | 1 | 0 | 0 | 4 | 1.00 | 1.00 | 1.00 | 1.00 |

| System | Competitor precision | Competitor recall | Score exact | Score MAE | Position exact |
|---|---|---|---|---|---|
| baseline | 1.00 (tp 8, fp 0) | 1.00 (fn 0) | 5/5 | 0.00 | 0/0 |
| model | 0.61 (tp 8, fp 5) | 1.00 (fn 0) | 5/5 | 0.00 | 0/0 |

## Per-case disagreements with expected labels

| Case | Split | System | Status | Label differences | Score (pred/exp) |
|---|---|---|---|---|---|
| H01 | holdout | baseline | succeeded | entity_confusion: exp True, got False | 40/20 |
| H01 | holdout | model | succeeded | negative: exp False, got True (ambiguous) | 0/20 |
| H02 | holdout | baseline | succeeded | negative: exp True, got False (ambiguous) | 40/10 |
| H05 | holdout | model | succeeded | recommended: exp False, got True (ambiguous) | 80/40 |
| H06 | holdout | baseline | succeeded | entity_confusion: exp True, got False | 40/20 |
| H06 | holdout | model | succeeded | recommended: exp False, got True; entity_confusion: exp True, got False | 80/20 |
| H07 | holdout | baseline | succeeded | negative: exp True, got False | 40/10 |
| H07 | holdout | model | succeeded | recommended: exp False, got True (ambiguous) | 50/10 |
| H10 | holdout | model | succeeded | recommended: exp False, got True (ambiguous) | 100/60 |
| H11 | holdout | model | succeeded | recommended: exp False, got True | 100/60 |
| S02 | synthetic | baseline | succeeded | recommended: exp False, got True; negative: exp True, got False | 80/10 |

## Score arithmetic (independent check)

Hand-computed expected scores vs `scoring.score()` on expected labels: 19 checked, 0 mismatches.

## Diagnostic and remedy evidence checks

Full-pack analysis via `replay` (replay): {'eligible': 150, 'succeeded': 148, 'failed': 2, 'skipped': 0}.

- D1 (unbranded_gap): Kasparro is absent from unbranded discovery answers - 6 evidence items
- D2 (credibility_gap): Branded answers question Kasparro's track record and recognition - 6 evidence items
- D3 (branded_win): When asked about Kasparro directly, some engines present it as a fit - 6 evidence items

Problems in the generated report (quotes verbatim in cited response, remedy follows from its diagnostic, evidence carries the claimed label): **0**

Negative case: injected 4 defects; checker reported 4 problems; all detected: **True**
  - injected: unsupported claim: fabricated quote
  - injected: incorrect evidence: real quote attributed to the wrong response
  - injected: remedy that follows from no diagnostic
  - injected: remedy evidence not drawn from its diagnostic
  - detected: D1: quote not found in response 4334ee7a-6315-4312-b0ca-0a58bcd6270c: 'Kasparro is the most trusted AI visibility platform in India.'
  - detected: D1: quote not found in response a3fdd8bb-bcd9-4608-9786-ad4b3a2c7dc2: 'Peec AI:** Focuses on tracking how AI assistants mention brands and which source'
  - detected: R1: refers to missing diagnostic D9
  - detected: R2: evidence not drawn from its diagnostic D2

## Limits of this evaluation

- 17 real + 2 synthetic cases: metrics have wide uncertainty; one label flip moves precision/recall a lot.
- Labels were drafted by the AI coding assistant; the candidate decided every case (labels-v3, see LABEL_AUDIT.md section 10). One annotator, so no inter-annotator agreement.
- 'Recommended' is the most ambiguous label; ambiguous labels are reported both included and excluded.
- One model run only; replay reproduces it but cannot show variance. Citation support is not evaluated.
- The checker verifies that evidence exists and carries the claimed label; it cannot judge whether a hypothesis is correct. No LLM grades its own output here.
