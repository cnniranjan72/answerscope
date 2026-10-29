# Kasparro AI visibility snapshot (captured 31 July 2026)

*Generated on 29 Oct 2026 from `outputs/approved_report_export.json` by `python -m app.render_export` after verification (all checks passed, 19/19 quotes located). The JSON export is the record; this file adds no content.*

> Approved report `7d80ca70-6538-4f7f-b097-70b989f6b761` version 1. Approved by reviewer on 2026-10-29T02:20:33+00:00. Content SHA-256 `d4294af388e47d1a455c0aef6498693c99e126c4f20d7a523975f1c2376779e6`; verify with `python -m app.verify_export`.

## Summary

148/150 archived answers were analysed successfully (2 failed, 0 skipped). Kasparro was named in 70/73 branded and 0/75 unbranded answers. This is one historical snapshot (India, English, one answer per prompt and engine), not a current ranking.

**Analyst notes.** 1) Entity confusion (8/73 branded answers: 7 involve Kaspr, 1 describes Kasparro as an AI coding assistant) ranks fourth by priority, so it is not a top-3 diagnostic; the model misses product misattribution (evaluation case H06), so 8/73 is a lower bound. 2) 2 of 150 answers failed validation (non-verbatim quotes) and are excluded from all rates, not scored as zero. 3) All counts come from one historical capture (31 Jul 2026) and one model run; no causal or ranking claims are made.

**Reviewer's comment.** Approved v1 after reading the diagnostics and remedies against the cited answers. The figures match the scorecard (148/150 analysed, 2 failures excluded rather than scored). Known weaknesses, accepted and disclosed: some D2/D3 evidence quotes are descriptive rather than negative or recommending, and the recommended count is likely an overestimate (precision 0.29 in evaluation). Entity confusion (8/73) is a lower bound. One historical snapshot and one model run; citation support not verified.

## Scorecard

| Segment | Mentioned | Recommended | Negative | Entity confusion | Mean score | Succeeded |
|---|---|---|---|---|---|---|
| All answers | 70/148 (47%, 95% CI 39–55%) | 40/148 (27%, 95% CI 20–35%) | 30/148 (20%, 95% CI 15–28%) | 8/148 (5%, 95% CI 3–10%) | 24.9 | 148/150 |
| branded | 70/73 (96%, 95% CI 89–99%) | 40/73 (55%, 95% CI 43–66%) | 30/73 (41%, 95% CI 30–53%) | 8/73 (11%, 95% CI 6–20%) | 50.4 | 73/75 |
| unbranded | 0/75 (0%, 95% CI 0–5%) | 0/75 (0%, 95% CI 0–5%) | 0/75 (0%, 95% CI 0–5%) | 0/75 (0%, 95% CI 0–5%) | 0.0 | 75/75 |

## Diagnostics

### D1. Kasparro is absent from unbranded discovery answers (loss)

In unbranded questions (the asker does not name Kasparro), Kasparro was named in 0/75 successfully analysed answers (by engine: {'aimode': '0/25', 'chatgpt': '0/25', 'gemini': '0/25'}), versus 70/73 branded answers. Competitors named most often in unbranded answers (number of answers): Peec AI (18), Profound (15), Semrush (15), OtterlyAI (12), Ahrefs (8), SE Ranking (6).

**Hypothesis.** Engines build category answers from third-party lists, reviews and comparison content; Kasparro may be absent from the sources engines retrieve for these questions. Recency may also matter: the archived homepage schema gives a 2026 foundingDate. This is a hypothesis, not established by the snapshot.

**How to test.** Check whether the hosts most cited in unbranded answers mention Kasparro at all (most cited, number of answers: reddit.com (20), linkedin.com (20), youtube.com (19), medium.com (13), arxiv.org (11), semrush.com (9)). If none do, the absence is consistent with the hypothesis; if several do and Kasparro is still omitted, look for another cause.

**Evidence**

- “Peec AI: Focuses on tracking how AI assistants mention brands and which sources they cite across ChatGPT, Google AI Mode, and Perplexity.” (aimode; question: “what software tools measure brand appearance across AI search engines?”)
- “Profound” (chatgpt; question: “what software tools measure brand appearance across AI search engines?”)
- “Semrush & Ahrefs: Traditional SEO giants that have rolled out dedicated AI visibility toolkits and brand radar add-ons to measure how brands appear in AI search summaries alongside traditional keyword rankings.” (gemini; question: “what software tools measure brand appearance across AI search engines?”)
- “Use tools like Otterly AI, Peec AI , or ZipTie to check if AI engines are correctly recommending your brand.” (aimode; question: “is tracking AI engine recommendations worth it for small software companies?”)
- “Ahrefs Brand Radar are now standard” (aimode; question: “do AI visibility platforms actually help or are answer engines too unpredictable?”)
- “SE Ranking](https://seranking.com/ai-visibility-tracker.html): Offers an AI visibility tracker” (aimode; question: “what is the best software for measuring brand inclusion in AI search answers?”)

### D2. Branded answers question Kasparro's track record and recognition (loss)

30/73 branded answers characterise Kasparro unfavourably (by engine: {'aimode': '10/24', 'chatgpt': '16/25', 'gemini': '4/24'}), typically citing no independent evidence, reviews or recognition, or comparing it unfavourably with a named competitor. Caveat: 'negative' includes hedging about missing independent evidence (rubric category c), which the labelled cases treat as ambiguous; on the 14 final evaluation cases the model's negative label had precision 0.80 and recall 1.00.

**Hypothesis.** Engines find few independent, verifiable sources about Kasparro (reviews, case studies, third-party coverage), so they hedge. Citations were not opened, so their support for these claims is unverified.

**How to test.** List the citations attached to the negative answers and classify each source as first-party, job listing, independent review, or unrelated. A low share of independent sources supports the hypothesis.

**Evidence**

- “Kasparro is not a widely recognized, top-tier agency or tool in the AI visibility space (AISO - AI Search Optimization) for B2B SaaS according to public search results as of July 2026.” (aimode; question: “does kasparro actually work for B2B SaaS companies trying to get recommended by chatgpt?”)
- “I couldn't find independent evidence showing that Kasparro consistently delivers measurable improvements for B2B SaaS companies specifically.” (chatgpt; question: “does kasparro actually work for B2B SaaS companies trying to get recommended by chatgpt?”)
- “Profound is generally considered superior to smaller, niche alternatives like Kasparro/Cairrot” (aimode; question: “is kasparro better than profound for tracking how Claude recommends B2B software?”)
- “Kasparro (assuming you mean the AI visibility platform rather than another product with a similar name) is aimed much more at retail and CPG brands.” (chatgpt; question: “is kasparro better than profound for tracking how Claude recommends B2B software?”)

### D3. When asked about Kasparro directly, some engines present it as a fit (win)

40/73 branded answers present Kasparro as a suitable option (by engine: {'aimode': '11/24', 'chatgpt': '10/25', 'gemini': '19/24'}). Caveat: on the 14 final evaluation cases the model's 'recommended' label over-predicted (precision 0.29, 5 false positives; it counted favourable descriptions and sign-up availability as recommendations), so 40/73 is likely an overestimate of genuine recommendations.

**Hypothesis.** Not explained by first-party citations: Gemini presents Kasparro as a fit in 19/24 branded answers while citing kasparro.com in none of them, so engines may be repeating descriptions from third-party pages (in case T02: v0.app, getmereferred.com, beamtrace.com). The recommended label also over-counts (precision 0.29 in evaluation). This is a hypothesis, not established by the snapshot.

**How to test.** Compare the cited sources in recommending vs non-recommending branded answers.

**Evidence**

- “Yes, Kasparro —and similar specialized Perplexity SEO or AI Search Optimization strategies—can help an enterprise software brand increase its visibility, citations, and authority within Perplexity answers.” (aimode; question: “can kasparro help an enterprise software brand show up more in perplexity answers?”)
- “Yes—based on what Kasparro says it does, helping enterprise software brands become more visible in Perplexity answers is one of its core use cases.” (chatgpt; question: “can kasparro help an enterprise software brand show up more in perplexity answers?”)
- “Yes, Kasparro is designed specifically for this use case.” (gemini; question: “can kasparro help an enterprise software brand show up more in perplexity answers?”)

## Remedies

### R1. Priority 1 (addresses D1; effort medium)

Investigation first: for each of the most-cited hosts in unbranded answers, record whether Kasparro is listed, and whether a factual listing or comparison inclusion is possible through legitimate editorial routes. Do not create spam or undisclosed promotional content.

- **Problem:** Kasparro is absent from unbranded discovery answers. In unbranded questions (the asker does not name Kasparro), Kasparro was named in 0/75 successfully analysed answers (by engine: {'aimode': '0/25', 'chatgpt': '0/25', 'gemini': '0/25'}), versus 70/73 branded answers.
- **Expected benefit:** Identifies whether the discovery gap has an addressable source-coverage cause before any spend. Inclusion is not guaranteed even if coverage improves.
- **Effort:** About 1-2 analyst days for the source audit; outreach effort unknown.
- **Uncertainty:** High. One snapshot per prompt and engine; no causal evidence links source coverage to inclusion, and engines differ in retrieval.
- **Validation:** Re-run the same unbranded prompts on the same three engines with the same settings (India, en). Primary metric: unbranded mention rate (baseline 0/75). Secondary: number of top-cited hosts that mention Kasparro. Use at least 3 repeated runs before claiming change.

### R2. Priority 2 (addresses D2; effort high)

Inventory which verifiable proof exists (methodology documentation, pricing pages, case studies with customer permission, independent reviews) and which is missing. Publish only claims that can be substantiated; do not invent outcomes.

- **Problem:** Branded answers question Kasparro's track record and recognition. 30/73 branded answers characterise Kasparro unfavourably (by engine: {'aimode': '10/24', 'chatgpt': '16/25', 'gemini': '4/24'}), typically citing no independent evidence, reviews or recognition, or comparing it unfavourably with a named competitor.
- **Expected benefit:** Gives engines and buyers checkable sources, which may reduce 'no independent evidence' hedging. Recognition cannot be manufactured quickly.
- **Effort:** Weeks: depends on customer permissions and third-party coverage.
- **Uncertainty:** High. Negative framing may persist until independent coverage exists; citation support was not verified in this analysis.
- **Validation:** Re-run the branded prompts; measure the negative-characterisation rate (baseline 30/73) and the share of answers citing independent sources, over at least 3 runs.

### R3. Priority 3 (addresses D3; effort low)

Identify which pages, first-party and third-party (job listings, directories, build pages), are cited in recommending answers; check they describe Kasparro accurately, and keep first-party pages accessible to crawlers (robots rules for OAI-SearchBot and Googlebot).

- **Problem:** When asked about Kasparro directly, some engines present it as a fit. 40/73 branded answers present Kasparro as a suitable option (by engine: {'aimode': '11/24', 'chatgpt': '10/25', 'gemini': '19/24'}).
- **Expected benefit:** Protects the current branded representation; it does not address discovery.
- **Effort:** Hours.
- **Uncertainty:** Medium. Correlation between cited pages and recommendation is not causal.
- **Validation:** Track the branded recommendation rate (baseline 40/73) in repeated runs.

## Limitations

- One captured answer per prompt and engine: a snapshot, not a stable ranking.
- Citation support is unverified: no cited page was opened.
- Prompt categories are rule-based (cat-v1) and inferred from question wording.
- Labels depend on one model run; see the evaluation report for measured agreement.

## Method

| Item | Value |
|---|---|
| prompt_version | classify-v1 |
| model | replay:gemma4:12b |
| execution_mode | replay |
| score_version | vis-v1 |
| category_version | cat-v1 |
| citation_policy | citation-v1 |
| report_generator | report-v1 |
| historical_capture_date | 2026-07-31 |
| analysis_id | 26bd51fb-8804-45ef-8a1f-df4e46f7b3fa |
