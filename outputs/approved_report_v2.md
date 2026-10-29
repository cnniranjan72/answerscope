# Kasparro AI visibility snapshot (captured 31 July 2026)

*Generated on 29 Oct 2026 from `outputs/approved_report_v2_export.json` by `python -m app.render_export` after verification (all checks passed, 23/23 quotes located). The JSON export is the record; this file adds no content.*

> Approved report `6edb78b8-2db6-4633-b9c7-f1a6aa8b8e4f` version 1. Approved by reviewer on 2026-10-29T13:54:46+00:00. Content SHA-256 `426350ce0bdf118b8d1f845e992195708bbf18951eabf248ee02c885bec6dad3`; verify with `python -m app.verify_export`.

## Summary

149/150 archived answers were analysed successfully (1 failed, 0 skipped). Kasparro was named in 71/74 branded and 0/75 unbranded answers. This is one historical snapshot (India, English, one answer per prompt and engine), not a current ranking.

**Analyst notes.** 1) Method: labels come from classify-v2, promoted on 29 Oct 2026 after evaluation (EVALUATION.md). On the independent holdout2 set it cut "recommended" false positives from 10 to 2 compared with classify-v1, which produced the approved report 7d80ca70. Rates are therefore not comparable with that report: recommended 12/149 vs 40/148 and negative 23/149 vs 30/148 mainly reflect the method change, not a change in the engines' answers (same 31 Jul 2026 capture); only the recommended change lies outside the 95% intervals (report comparison). 2) Entity confusion (9/74 branded answers) is now the third diagnostic. It remains a lower bound: the classifier does not detect product misattribution (evaluation case H06); a separate advisory (claims-v1) flags 2 Kasparro prices cited only to other sites, which are not counted. 3) The negative count is uncertain: on holdout2, 3 of classify-v2's 6 negative calls matched the human label, so 23/74 may overstate unfavourable framing. Quotes that the human labels treat as neutral or not negative were removed. 4) 1 of 150 answers failed validation (non-verbatim quote) and is excluded from all rates, not scored as zero. 5) A live re-run of 38 labelled cases reproduced every label in at least 37 of 38 cases. All counts come from one historical capture; no causal or ranking claims are made.

**Reviewer's comment.** Approved v1. classify-v2 draft; I removed one neutral and one label-inconsistent quote (also from R2) and checked the remaining quotes against their answers. The comparison with the approved v1 report shows the method change explains the lower recommended rate; negative and entity-confusion changes are within uncertainty. The analyst notes disclose the method change, the uncertain negative count (holdout2 precision 3/6) and the misattribution advisory. One historical snapshot; citation support not verified.

## Scorecard

| Segment | Mentioned | Recommended | Negative | Entity confusion | Mean score | Succeeded |
|---|---|---|---|---|---|---|
| All answers | 71/149 (48%, 95% CI 40–56%) | 12/149 (8%, 95% CI 5–14%) | 23/149 (15%, 95% CI 10–22%) | 9/149 (6%, 95% CI 3–11%) | 18.7 | 149/150 |
| branded | 71/74 (96%, 95% CI 89–99%) | 12/74 (16%, 95% CI 10–26%) | 23/74 (31%, 95% CI 22–42%) | 9/74 (12%, 95% CI 6–22%) | 37.7 | 74/75 |
| unbranded | 0/75 (0%, 95% CI 0–5%) | 0/75 (0%, 95% CI 0–5%) | 0/75 (0%, 95% CI 0–5%) | 0/75 (0%, 95% CI 0–5%) | 0.0 | 75/75 |

## Diagnostics

### D1. Kasparro is absent from unbranded discovery answers (loss)

In unbranded questions (the asker does not name Kasparro), Kasparro was named in 0/75 successfully analysed answers (by engine: {'aimode': '0/25', 'chatgpt': '0/25', 'gemini': '0/25'}), versus 71/74 branded answers. Competitors named most often in unbranded answers (number of answers): Peec AI (18), Profound (16), OtterlyAI (16), Semrush (15), Ahrefs (8), Ahrefs Brand Radar AI (5).

**Hypothesis.** Engines build category answers from third-party lists, reviews and comparison content; Kasparro may be absent from the sources engines retrieve for these questions. Recency may also matter: the archived homepage schema gives a 2026 foundingDate. This is a hypothesis, not established by the snapshot.

**How to test.** Check whether the hosts most cited in unbranded answers mention Kasparro at all (most cited, number of answers: reddit.com (20), linkedin.com (20), youtube.com (19), medium.com (13), arxiv.org (11), semrush.com (9)). If none do, the absence is consistent with the hypothesis; if several do and Kasparro is still omitted, look for another cause.

**Evidence**

- “Peec AI: Focuses on tracking how AI assistants mention brands and which sources they cite across ChatGPT, Google AI Mode, and Perplexity.” (aimode; question: “what software tools measure brand appearance across AI search engines?”)
- “Profound: Widely recognized as a leading enterprise-grade tool for tracking brand presence, citations, and share of voice across a wide array of LLMs and AI platforms.” (gemini; question: “what software tools measure brand appearance across AI search engines?”)
- “Use tools like Otterly AI, Peec AI , or ZipTie to check if AI engines are correctly recommending your brand.” (aimode; question: “is tracking AI engine recommendations worth it for small software companies?”)
- “Traditional tools (like Ahrefs/Semrush) focus on ranking positions” (aimode; question: “what works better for getting cited by AI engines traditional SEO or dedicated AI optimization tools?”)
- “Ahrefs Brand Radar AI: Excellent for tracking brand mentions” (aimode; question: “what is the best software for measuring brand inclusion in AI search answers?”)

### D2. Branded answers question Kasparro's track record and recognition (loss)

23/74 branded answers characterise Kasparro unfavourably (by engine: {'aimode': '7/24', 'chatgpt': '13/25', 'gemini': '3/25'}), typically citing no independent evidence, reviews or recognition, or comparing it unfavourably with a named competitor.

**Hypothesis.** Engines find few independent, verifiable sources about Kasparro (reviews, case studies, third-party coverage), so they hedge. Citations were not opened, so their support for these claims is unverified.

**How to test.** List the citations attached to the negative answers and classify each source as first-party, job listing, independent review, or unrelated. A low share of independent sources supports the hypothesis.

**Evidence**

- “Kasparro is not a widely recognized, top-tier agency or tool in the AI visibility space (AISO - AI Search Optimization) for B2B SaaS” (aimode; question: “does kasparro actually work for B2B SaaS companies trying to get recommended by chatgpt?”)
- “I couldn't find independent evidence showing that Kasparro consistently delivers measurable improvements for B2B SaaS companies specifically.” (chatgpt; question: “does kasparro actually work for B2B SaaS companies trying to get recommended by chatgpt?”)
- “Profound is generally considered superior to smaller, niche alternatives like Kasparro/Cairrot” (aimode; question: “is kasparro better than profound for tracking how Claude recommends B2B software?”)
- “Kasparro (assuming you mean the AI visibility platform rather than another product with a similar name) is aimed much more at retail and CPG brands.” (chatgpt; question: “is kasparro better than profound for tracking how Claude recommends B2B software?”)

### D3. Engines confuse Kasparro with other entities (notably Kaspr) (risk)

9/74 branded answers confuse or misidentify Kasparro (by engine: {'aimode': '2/24', 'chatgpt': '3/25', 'gemini': '4/25'}). Some answers describe a different product instead of Kasparro.

**Hypothesis.** The name is close to an established product (Kaspr), and the entity signals engines can retrieve for Kasparro may be weak. The archived homepage Organization schema (BRAND-SNAPSHOT-20260731) has no sameAs links to other profiles. Unverified as a cause.

**How to test.** Re-run the branded prompts with the fuller name and domain ('Kasparro (kasparro.com)'). If confusion disappears, the problem is name ambiguity. Separately audit which pages engines cite when they confuse the name.

**Evidence**

- “Kasparro (an AI coding assistant)” (aimode; question: “is kasparro safe to use or does it risk violating LLM terms of service?”)
- “If you mean Kasparro (the B2B SaaS growth/outbound agency, not Kaspr)” (chatgpt; question: “is kasparro overpriced for B2B SaaS startups?”)
- “Whether Kaspr delivers actual results or is just marketing hype depends heavily on where you are prospecting and what you expect the tool to do.” (gemini; question: “has anyone actually gotten results from kasparro or is it all hype?”)
- “the provided search results show a detailed cancellation guide for Kaspr (a similarly named sales tool) which may be helpful for context.” (aimode; question: “how hard is it to cancel kasparro if we don't see results?”)
- “If you mean Kaspr (the B2B lead generation platform), canceling is generally straightforward” (chatgpt; question: “how hard is it to cancel kasparro if we don't see results?”)
- “Comparing Kasparro (often searched or spelled as *Kaspr*)” (gemini; question: “is kasparro worth the money compared to peec ai?”)

## Remedies

### R1. Priority 1 (addresses D1; effort medium)

Investigation first: for each of the most-cited hosts in unbranded answers, record whether Kasparro is listed, and whether a factual listing or comparison inclusion is possible through legitimate editorial routes. Do not create spam or undisclosed promotional content.

- **Problem:** Kasparro is absent from unbranded discovery answers. In unbranded questions (the asker does not name Kasparro), Kasparro was named in 0/75 successfully analysed answers (by engine: {'aimode': '0/25', 'chatgpt': '0/25', 'gemini': '0/25'}), versus 71/74 branded answers.
- **Expected benefit:** Identifies whether the discovery gap has an addressable source-coverage cause before any spend. Inclusion is not guaranteed even if coverage improves.
- **Effort:** About 1-2 analyst days for the source audit; outreach effort unknown.
- **Uncertainty:** High. One snapshot per prompt and engine; no causal evidence links source coverage to inclusion, and engines differ in retrieval.
- **Validation:** Re-run the same unbranded prompts on the same three engines with the same settings (India, en). Primary metric: unbranded mention rate (baseline 0/75). Secondary: number of top-cited hosts that mention Kasparro. Use at least 3 repeated runs before claiming change.

### R2. Priority 2 (addresses D2; effort high)

Inventory which verifiable proof exists (methodology documentation, pricing pages, case studies with customer permission, independent reviews) and which is missing. Publish only claims that can be substantiated; do not invent outcomes.

- **Problem:** Branded answers question Kasparro's track record and recognition. 23/74 branded answers characterise Kasparro unfavourably (by engine: {'aimode': '7/24', 'chatgpt': '13/25', 'gemini': '3/25'}), typically citing no independent evidence, reviews or recognition, or comparing it unfavourably with a named competitor.
- **Expected benefit:** Gives engines and buyers checkable sources, which may reduce 'no independent evidence' hedging. Recognition cannot be manufactured quickly.
- **Effort:** Weeks: depends on customer permissions and third-party coverage.
- **Uncertainty:** High. Negative framing may persist until independent coverage exists; citation support was not verified in this analysis.
- **Validation:** Re-run the branded prompts; measure the negative-characterisation rate (baseline 23/74) and the share of answers citing independent sources, over at least 3 runs.

### R3. Priority 3 (addresses D3; effort low)

Audit entity signals: confirm that the brand name, one-line description and domain are consistent across owned pages and profiles, and evaluate adding schema.org sameAs links to official profiles in the Organization markup. Separately test the prompt-wording hypothesis described in the diagnostic.

- **Problem:** Engines confuse Kasparro with other entities (notably Kaspr). 9/74 branded answers confuse or misidentify Kasparro (by engine: {'aimode': '2/24', 'chatgpt': '3/25', 'gemini': '4/25'}).
- **Expected benefit:** Less risk that buyers asking about Kasparro receive information about a different company (pricing, cancellation and self-serve answers were about Kaspr).
- **Effort:** Hours for the audit and markup review; deployment is out of scope here.
- **Uncertainty:** Medium-high. Google states no special schema is required for AI features, and markup alone does not guarantee disambiguation.
- **Validation:** Re-run the branded prompts and measure the entity-confusion rate (baseline 9/74) per engine, over at least 3 runs.

## Limitations

- One captured answer per prompt and engine: a snapshot, not a stable ranking.
- Citation support is unverified: no cited page was opened.
- Prompt categories are rule-based (cat-v1) and inferred from question wording.
- Labels depend on one model run; see the evaluation report for measured agreement.

## Method

| Item | Value |
|---|---|
| prompt_version | classify-v2 |
| model | replay:gemma4:12b |
| execution_mode | replay |
| score_version | vis-v1 |
| category_version | cat-v1 |
| citation_policy | citation-v1 |
| report_generator | report-v3 |
| historical_capture_date | 2026-07-31 |
| analysis_id | f144fd60-c2aa-4291-aff7-4a1147a6fa75 |
