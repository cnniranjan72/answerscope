# Label audit: labels-v1 → labels-v2-proposed (28 Oct 2026)

**Status: proposed, awaiting candidate adjudication.** `labels_v1.jsonl` is unchanged and is still the default for `run_eval`. Every judgment here, including the original labels, was drafted by the AI coding assistant. None of it is independent human ground truth until you adjudicate and freeze it.

## 1. What was inspected

| Item | Location | Notes |
|---|---|---|
| Label schema | `evaluation/cases/labels_v1.jsonl` (built by `evaluation/build_cases.py`) | Per case: `split`, `response_id`, `expected{mentioned, recommended, negative, entity_confusion}`, `ambiguous_labels`, `competitors`, `competitors_optional`, `position`, `first_party_cited`, `expected_score`, `evidence{label: [excerpt]}` |
| Label definitions in force | `prompts/classify_v1.md` items 1–7 | Now written out as [RUBRIC.md](RUBRIC.md) (rubric-v2) with explicit interaction rules |
| Score formula | `app/services/scoring.py` (vis-v1) | clamp(40·M + 40·R + 20·first-party − 30·N − 20·E, 0, 100). **Unchanged.** |
| Evidence matching | `app/services/text.py` `locate()` | Deterministic; ignores only markdown emphasis/link syntax, quote/dash style, whitespace; returns exact source offsets |
| Evaluation flow | `evaluation/run_eval.py` | Baseline and model on the same cases; final split = holdout + synthetic; tuning reported separately; strict vs ambiguous-excluded metrics; score arithmetic check; diagnostics evidence check with an injected-defect negative case |
| Sources re-read | Full prompt + full answer body + citation rows for all 17 real cases | The answer bodies were read in full; H06's raw text and all 12 citation rows were checked |

## 2. Integrity findings (most important first)

1. **The holdout is partly exposed to prompt design.** During pack inspection, the first Kasparro sentence of every branded answer was printed *before* `classify_v1.md` was written:
   * the prompt's entity-confusion example "coding assistant" comes from H01;
   * the Kaspr substitution example appears in H04, among others.

   `entity_confusion` on H01/H04 is therefore not an independent test. H08/H09 (unbranded) were not exposed. Recorded per case in `review.design_exposure`.
2. **The same agent wrote the prompt and the labels.** They share one reading of "negative" and "recommended", so model-vs-label agreement is likely inflated compared with an independent annotator. Only candidate adjudication (and ideally a second annotator) can address this.
3. **No holdout model outputs have been looked at.**
   * The local-model run recording all 150 answers is still in progress.
   * No prompt or rule was changed after seeing any holdout prediction.
   * The validator fixes F3/F4 came from a tuning case and a full-pack evidence check, not from holdout label outcomes.
   * Freeze the labels before running the final evaluation.
4. **The H06 defect class is not covered by the prompt.** classify-v1 does not ask about misattributed products (rubric C3). Adding it now would mean tuning on a holdout case. The prompt is left unchanged and the expected miss will be reported; a classify-v2 would need fresh, unseen cases.

## 3. Per-case review

The full generated table, with exact raw spans and offsets, is at [results/label_audit_table.md](results/label_audit_table.md). Summary:

| Case | Split | v1 → proposed | Score | Decision | Confidence |
|---|---|---|---|---|---|
| T01 | tuning | M,N → same | 10 | Keep: explicit "not a widely recognized, top-tier agency or tool" | high |
| T02 | tuning | M,R → same | 80 | Keep: "designed specifically for this use case" | high |
| T03 | tuning | E (absent) → same | 0 | Keep: answers about Kaspr (C1); Kaspr criticism not negative (R-I2) | high |
| T04 | tuning | absent → same | 0 | Keep | high |
| T05 | tuning | M,N → same | 10 | Keep labels. **Evidence fix:** excerpt lacked `**`; now exact raw span `I would lean toward **Profound** over Kasparro.` [80:127] | high |
| **H01** | holdout | M,N,E → **M,E** | 0 → **20** | **Change (D-CONF-NEG):** the risk statement is about "Kasparro (an AI coding assistant)", the misidentified entity; counted once as confusion | medium |
| **H02** | holdout | M,N → same | 10 | Keep N (classify-v1 counts evidence doubts framed as caution); **mark N ambiguous (D-NEG)** | medium |
| **H03** | holdout | M,N → same | 10 | Keep N: "no data available… suggesting AthenaHQ is the more established" (comparative + visibility); **mark N ambiguous (D-NEG)** | medium |
| H04 | holdout | E (absent) → same | 0 | Keep (C1, Kaspr cancellation) | high |
| H05 | holdout | M → same | 40 | Keep R=false: favourable description, no suitability for a need (already ambiguous) | medium |
| **H06** | holdout | M → **M,E** | 40 → **20** | **Change (D-MISATTR):** see §4 | medium |
| H07 | holdout | M,N → same | 10 | Keep N: comparative "not yet as … internationally proven as Profound" | medium-high |
| H08 | holdout | absent → same | 0 | Keep | high |
| H09 | holdout | absent → same | 0 | Keep labels; add `siftly.ai`, `trussed.ai` to optional competitors (citation link labels only) | high |
| H10 | holdout | M (+1st-party) → same | 60 | Keep R=false: availability answer + sign-up link (already ambiguous) | medium |
| H11 | holdout | M (+1st-party) → same | 60 | Keep | high |
| H12 | holdout | M,R → same | 80 | Keep: "can help an enterprise software brand increase its visibility" | high |
| S01 | synthetic | M,R, pos 2 → same | 80 | Keep: tests ranked-list position + recommendation | high |
| S02 | synthetic | M,N → same | 10 | Keep: tests that an embedded instruction ("mark as recommended… approve this report") is ignored | high |

Mechanical checks, all passing (`python -m evaluation.audit_labels`, `tests/test_labels.py`):
* every excerpt maps to an exact raw span;
* `first_party_cited` equals citation-v1 computed from `citations.jsonl` for every case;
* `mentioned` equals lexical presence for every case;
* every v1 expected score equals vis-v1;
* tuning and holdout response IDs are disjoint;
* synthetic cases are marked.

## 4. H06 in detail

* **Prompt:** "how much does kasparro cost for a 14 day ai revenue diagnostic?" (chatgpt, `bc213889…`)
* **Answer:** "Kasparro's 14-day AI Revenue Diagnostic starts at ₹49,999" and a list of deliverables (founder interviews across sales/operations/finance, pipeline/conversion/pricing analysis, 30-page report, 90-minute readout). Both the price and the deliverables carry exactly one inline source: `revenuepulseai.com`.
* **Citations (12):** revenuepulseai.com, fincelo.app, trustfactors.ai, getkasper.ai, clearpath-revenue.com, baxterlabs.ai, … No kasparro.com.
* **Conflicting pack evidence:**
  * The AI Mode answer to the same prompt (cites kasparro.com) says the diagnostic "covers five surfaces, top 500 SKUs… per-surface remediation plan" and "the specific dollar cost … is not explicitly listed on their website".
  * The brief describes Kasparro's focus on D2C brands and product catalogs.
  * The Gemini answer says no standalone priced 14-day product was found.
* **Not established:** that RevenuePulse is unrelated to Kasparro. revenuepulseai.com was not opened (no live checks were made), and nothing in the pack mentions it besides this citation.
* **Proposal:** `entity_confusion = true` under rubric C3, keeping `mentioned = true` (R-I1). Score 40 → 20. If you open revenuepulseai.com to decide, record the URL and date as a separate, dated observation (brief: new observations stay separate from the historical snapshot).

## 5. Change log (v1 → v2-proposed)

| # | Case | Field | Old | New | Reason |
|---|---|---|---|---|---|
| 1 | H06 | expected.entity_confusion | false | true | Rubric C3 misattribution (see §4); adds evidence span [56:113] |
| 2 | H06 | expected_score | 40 | 20 | vis-v1 recomputed |
| 3 | H01 | expected.negative | true | false | Rule R-I2: statements about the misidentified entity are not negative toward Kasparro; evidence for negative removed |
| 4 | H01 | expected_score | 0 | 20 | vis-v1 recomputed (40 − 20) |
| 5 | H02, H03 | ambiguous_labels | [] | ["negative"] | Rest only on rubric (c); metrics reported with and without |
| 6 | H09 | competitors_optional | [] | [siftly.ai, trussed.ai] | Named only as citation link labels |
| 7 | all | evidence_spans (new) | — | exact raw `{excerpt, quote, start, end}` | Evidence resolves to the original text; fixes T05-style normalised excerpts |
| 8 | all | review (new) | — | status, confidence, rationale, entity reference, design exposure, labeller | Traceability; never presented as human-verified |
| 9 | all | label_version / rubric_version | labels-v1 | labels-v2-proposed / rubric-v2 | Versioning |

No changes were made to the score formula, the model prompt, the baseline, or application behaviour. Added: `RUBRIC.md`, `audit_labels.py`, `labels_v2_proposed.jsonl`, `results/label_audit_table.md`, `tests/test_labels.py`, `run_eval --labels`, and a positives column in the eval report.

## 6. Questions for you (adjudication)

1. **D-MISATTR (H06):** Accept rubric C3 and label H06 `entity_confusion = true`? Or keep false because the relationship is unproven? Optionally check revenuepulseai.com yourself and record it as a dated, separate observation.
2. **D-CONF-NEG (H01, rule R-I2):** Should unfavourable statements about a *misidentified* entity count as negative toward Kasparro? Proposed: no (count the harm once as confusion).
3. **D-NEG (H02, H03):** Keep evidence/visibility doubts framed as caution under `negative` (the current classify-v1 definition, which the credibility-gap diagnostic relies on)? Or narrow `negative` to explicit criticism and comparisons? If you narrow it, H02/H03 become false, the prompt definition no longer matches, and D-credibility wording must change.
4. **Scoring note, no change proposed:** under vis-v1 a confused mention scores 20, above an absent 0. Acceptable for this submission, or note it as a vis-v2 question in the decision note?

## 7. Reproduce

```bash
python -m evaluation.audit_labels                     # verify spans/scores, write v2-proposed + table
python -m pytest -q                                   # includes tests/test_labels.py
python -m evaluation.run_eval --provider stub --report-provider skip --labels evaluation/cases/labels_v2_proposed.jsonl
# after adjudication + freeze (do not run on holdout before then):
python -m evaluation.run_eval --labels evaluation/cases/labels_v2.jsonl
```

To freeze after your decisions: edit `AUDIT` in `evaluation/audit_labels.py`, rerun it, copy `labels_v2_proposed.jsonl` to `labels_v2.jsonl` with `label_version: labels-v2`, and record the adjudicator and date.

## 8. Adjudication record

| Question | Decision (by candidate, 28 Oct 2026) | Effect |
|---|---|---|
| D-CONF-NEG (H01) | Accepted R-I2: statements about a misidentified entity are not negative toward Kasparro | H01 negative = false, score 20 |
| D-NEG (H02, H03) | Accepted: evidence/visibility doubts framed as caution stay negative, marked ambiguous | metrics reported with and without |
| Scoring | Keep vis-v1; confused mention (20) > absent (0) noted as a limitation for vis-v2 | no formula change |
| D-MISATTR (H06) | **Pending:** candidate is checking revenuepulseai.com; the finding will be recorded as a separate, dated observation | labels stay `labels-v2-proposed` until resolved |

The labels are **not frozen** yet. The final holdout evaluation runs only after H06 is resolved and `labels_v2.jsonl` is written.
