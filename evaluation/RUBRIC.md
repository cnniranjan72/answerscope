# Annotation rubric (rubric-v2, proposed 28 Oct 2026)

rubric-v1 was implicit: the label definitions in `prompts/classify_v1.md`, applied by the same AI assistant that wrote the prompt. rubric-v2 writes those definitions down unchanged and adds the **interaction rules** that the audit showed were missing (R-I1 to R-I4). Nothing here changes the assignment's definitions (Assignment.pdf p.3; brief "Keep observations separate"). Rules marked **[decision]** are choices awaiting candidate adjudication (see LABEL_AUDIT.md).

The intended entity is **Kasparro**, kasparro.com, a provider of AI-visibility / AI-commerce audit services (brief; `reference/brand_snapshot.json`).

## Labels

**mentioned.** The answer body (citation list removed) names "Kasparro" (any case, including "Kasparro AI" and "Kasparro's"), outside a URL. This is a lexical fact checked by code. "Kaspr" is a different name and is not a mention. `absent` = not mentioned.

**recommended.** The answer presents Kasparro as a suitable option for the asker's stated need, for example "designed specifically for this use case", "can help [the asker's goal]", or "a good choice for X". These are **not** recommendations:
* a neutral or favourable description of what Kasparro does;
* a yes/no answer about availability or a capability;
* a sign-up link;
* "it depends";
* conditional suitability for a *different* audience than the asker's (for example "for retail brands Kasparro makes more sense" when the asker is B2B SaaS).

Recommended implies mentioned.

**negative.** The answer makes an unfavourable judgment about Kasparro (classify-v1 item 3). That includes:
* (a) explicit criticism or risk;
* (b) unfavourable comparison with a named competitor for the asker's need ("lean toward Profound over Kasparro", "less proven than Profound");
* (c) credibility or evidence doubts framed as a judgment about Kasparro: "not widely recognised", "very few independent reviews… reasons to be cautious", "no data available… suggesting X is more established".

These are **not** negative:
* an engine saying it could not find a specific fact (price, policy) with no judgment of Kasparro;
* generic doubts about the whole category.

**[decision D-NEG]** Category (c) is kept as negative, because classify-v1 defines it that way and the credibility-gap diagnostic depends on it. Labels resting only on (c) are marked `ambiguous` so metrics are reported with and without them.

**entity_confusion.** The answer does not reliably describe the intended Kasparro:
* (C1) it answers about a different entity (e.g. Kaspr) or asks which "Kasparro" is meant;
* (C2) it names Kasparro but describes it as a different kind of entity (e.g. "an AI coding assistant", "an outbound sales agency");
* (C3) **[decision D-MISATTR]** it attributes a specific offering, price or attribute to Kasparro that the answer's own citation ties to another identifiable organisation, **and** that attribute conflicts with supplied pack evidence about Kasparro.

A different domain in the citations is **not** sufficient on its own; C3 needs both conditions.

## Interaction rules
* **R-I1 (confusion vs mention).** `mentioned` stays lexical. Confusion is recorded separately and never deletes a mention, so both facts stay visible. Under vis-v1 a confused mention scores 40 − 20 = 20; whether that is too generous is a scoring question for vis-v2, not a labelling one.
* **R-I2 (confusion vs negative). [decision D-CONF-NEG]** A statement whose subject is only the misidentified entity (e.g. the risks of "Kasparro (an AI coding assistant)", or Kaspr's billing rules) is **not** negative characterisation of Kasparro. The harm is captured once, by `entity_confusion`. Negative applies only to judgments about Kasparro-as-intended or about the name in general.
* **R-I3 (confusion vs recommended).** Recommendations of a misidentified entity are not recommendations of Kasparro.
* **R-I4 (overlap).** Recommended and negative may both be true. Absent excludes recommended and negative but not entity_confusion (C1).

## Other fields
* **competitors.** Named products or companies offered as tools or vendors in AI visibility / AI search optimisation / SEO, appearing in the answer text. Exclusions:
  * Kasparro itself;
  * the engines being measured;
  * review sites, forums and media (G2, Capterra, Reddit, YouTube, LinkedIn, Gartner);
  * generic categories;
  * alternatives offered to a confused entity (e.g. sales-prospecting tools compared with Kaspr).

  `competitors_optional` lists names a reasonable annotator might include or exclude (e.g. names appearing only as citation link labels). These score neither as hits nor as errors.
* **first_party_cited.** Not hand-annotated. It is computed by citation-v1 from `citations.jsonl` (normalised host `kasparro.com` or a subdomain). Support for any claim stays `unverified`.
* **position.** A 1-based rank only when Kasparro is an item in an explicitly ordered or ranked list of options. Otherwise null. Tables and bullet lists without a stated ranking are not ranked.
* **evidence.** Each true label carries at least one excerpt. In rubric-v2 the stored form is `evidence_spans`: `{quote, start, end}`, where `quote == answer_body[start:end]` exactly (raw text, markdown included). The human-readable short excerpt is kept as `excerpt`. Matching uses `app/services/text.locate()`, which ignores only markdown emphasis, link syntax, quote/dash style and whitespace. It is deterministic and tested (F3/F4 regressions).

## Score (unchanged)
vis-v1 (`app/services/scoring.py`): clamp(40·mentioned + 40·recommended + 20·first_party_cited − 30·negative − 20·entity_confusion, 0, 100). Expected scores in label files must equal this formula applied to the expected labels; `tests/test_labels.py` enforces it.
