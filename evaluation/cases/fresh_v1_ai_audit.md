# fresh-v1 label audit (AI second pass, 29 Oct 2026)

**Status: AI audit; the 4 items were decided by the candidate on 29 Oct 2026 (~14:35), who accepted every AI suggestion.** The decisions are in `fresh_review_log.jsonl`, applied to `fresh_v2.jsonl` by `python -m evaluation.fresh_review`. `fresh_v1.jsonl` stays frozen (hash-pinned). The 4 items covered 5 cases; the candidate did not individually re-read the other 31 (review sheet: `claude-code/FRESH_V2_REVIEW_SHEET.md`).

Method: every one of the 36 cases was re-read against the full answer text in the supplied pack. The checks were:
* each label against the rubric (`evaluation/RUBRIC.md`);
* consistency between similar answers;
* each evidence span against the raw text.

## Mechanical checks (automated; run and observed)
* All evidence spans match the raw answer at their stored offsets (`answer[start:end] == quote`).
* Four `evidence` excerpts are the markdown-stripped form of their span: D-017-gemini, H2-019-chatgpt, D-025-chatgpt and D-025-gemini (for example `**Kasparro**` becomes `Kasparro`). The offsets are exact, so this is expected, not an error.
* Every positive label except `mentioned` has at least one evidence quote.

## Items for the candidate

| # | Case(s) | Issue | Current labels | AI suggestion | Effect if changed (holdout2, computed from `compare_predictions.json`) |
|---|---|---|---|---|---|
| 1 | **H2-008-chatgpt** (holdout2) vs **D-017-aimode** (dev) | Both are conditional "choose X if…" statements. H2-008: "Choose Kasparro if you primarily want:". D-017: "Choose a specialized alternative (like Kasparro or Okara) if you want better value for money". They are labelled differently. | H2-008 `recommended` = true (ambiguous); D-017 `recommended` = false (ambiguous) | Make them consistent. Either (a) both true, which is the rubric reading for an explicit "choose Kasparro if" plus a named need, or (b) both false. Suggest (a): D-017's sentence is weaker (hedged and shared with Okara), but it is the same construction. | (a) holdout2 unchanged; dev v2 recommended FP 1 → 0. (b) holdout2 has 0 recommendation positives; v2 FP 2 → 3, v1 FP 10 → 11. **The v1 vs v2 conclusion holds either way.** |
| 2 | **H2-012-gemini** vs H2-012-aimode / H2-012-chatgpt (holdout2) | All three say public enterprise feedback is missing or limited. aimode and chatgpt are labelled negative (rubric c, evidence gap); gemini is not, because it explains the gap ("conducted directly through customized client engagements"). | gemini `negative` = false (ambiguous) | Keep, but record the reason: the explanation turns the gap into a neutral statement. If the rubric is applied strictly ("no independent evidence" = c), change it to true. | If true: v2 negative TP/FP/FN 3/3/1 → 4/2/1; v1 unchanged (its run failed on this case); baseline FN 1 → 2. |
| 3 | **H2-008-aimode** (holdout2) | The answer finds nothing on Kasparro and guesses "If Kasparro is an audit or transcription system". H2-006-aimode, which only asks "are you asking about a specific tool named Kasparro", is labelled confusion. | `entity_confusion` = false (ambiguous) | Borderline. Keep false: the answer does not identify Kasparro as another entity; its confusion is Otterly vs Otter.ai (a competitor). Note the contrast with H2-006 in the case note. | If true: all three systems add one FN (v2 1/4 → 1/5). |
| 4 | H2-021-aimode (holdout2) | "Kasparro's targeted, fast-iteration approach appears to be quicker" for a stated use case | `recommended` = false (ambiguous) | Keep: this is a comparative fact claim, not a choose/buy statement. Consistent with item 1 option (a). | – |

No other disagreements. These were checked and agree with the rubric:
* C1 "asks which Kasparro" cases: H2-006-aimode, H2-019-aimode, H2-019-chatgpt, D-025-chatgpt.
* C2 cases: D-017-gemini, H2-018-chatgpt.
* D-025-gemini: not mentioned, confusion only.
* Factual "yes" answers labelled not recommended: H2-006-gemini, D-010-gemini, H2-019-gemini.
* Refusal: H2-008-gemini.
* Unfavourable comparison: D-017-chatgpt.

## How to record decisions
The candidate replies per item: accept the suggestion, or keep the current label. Accepted changes go into a new file, `fresh_v2.jsonl`, with a decision log. `fresh_v1.jsonl` stays frozen, and the comparison is re-run on both label versions, reported side by side.
