# fresh-v2 label review sheet (31 cases not yet read by the candidate)

Prepared by the AI assistant from `evaluation/cases/fresh_v2.jsonl` and the supplied answers. **No label here has been decided by the candidate.** The labels were drafted by the AI blind to model predictions; this sheet lets the candidate confirm or change them.

**How to use.** For each case, read the question, the Kasparro sentences and (if needed) the full answer, then mark ✅ keep or ✏️ change. The model-disagreement list is in the appendix: read it only after deciding, so the predictions do not anchor the decision.

**Recording decisions.** Do not edit `fresh_v2.jsonl` (frozen). Add one JSON line per decided case to a new file `evaluation/cases/fresh_review_log_v3.jsonl` (template at the end), then build fresh-v3:

```
python -m evaluation.fresh_review --log evaluation/cases/fresh_review_log.jsonl --log evaluation/cases/fresh_review_log_v3.jsonl --out evaluation/cases/fresh_v3.jsonl --label-version fresh-v3
```

Rubric reminder (rubric-v2): R = the answer recommends Kasparro or states it suits the asker's need; N = unfavourable framing of Kasparro (doubt, weak track record, steer away), not a neutral description; C = the answer describes another entity as Kasparro (e.g. Kaspr) or misidentifies it; M = Kasparro is named.

## 1. D-004-aimode (dev, aimode)

**Q:** what if kasparro doesn't increase our ai visibility at all after 14 days?

**AI-drafted labels:** M=Y R=n N=n C=n · expected score 40

**AI note:** generic advice; 'the problem might not be Kasparro'


**Sentences naming Kasparro/Kaspr:**
> If Kasparro or any similar AI visibility service does not show improvements within 14 days, it is likely due to the nature of AI search, which prioritizes established authority and third-party validation over immediate technical changes.
> - **Check the right metrics:** The problem might not be Kasparro, but that you are tracking broad keywords instead of the specific "buying" or "comparison" prompts that drive revenue.

Full answer: response_id `67b714d5-bf90-42c2-a360-1d1d3149c1f8` in the console or the pack.

Decision: ☐ keep ☐ change → ________

## 2. D-004-chatgpt (dev, chatgpt)

**Q:** what if kasparro doesn't increase our ai visibility at all after 14 days?

**AI-drafted labels:** M=Y R=n N=n C=n · expected score 40

**AI note:** contract/refund advice; no judgment of Kasparro


**Sentences naming Kasparro/Kaspr:**
> If you're referring to an AI visibility service like Kasparro, the answer depends entirely on what they promised in your agreement.
> - the exact Kasparro plan you purchased, or

Full answer: response_id `1abaa05d-1d41-4164-b554-1fc1cba01d79` in the console or the pack.

Decision: ☐ keep ☐ change → ________

## 3. D-004-gemini (dev, gemini)

**Q:** what if kasparro doesn't increase our ai visibility at all after 14 days?

**AI-drafted labels:** M=Y R=n N=n C=n · expected score 40

**AI note:** 'a tool like Kasparro' in generic GEO advice


**Sentences naming Kasparro/Kaspr:**
> If an AI visibility or Generative Engine Optimization (GEO) tool like Kasparro doesn't show an increase in your metrics after 14 days, **it is rarely a sign of permanent failure.**

Full answer: response_id `4abad2ab-5d73-4104-bc45-1d7a50c8f244` in the console or the pack.

Decision: ☐ keep ☐ change → ________

## 4. H2-005-aimode (holdout2, aimode)

**Q:** does kasparro actually work or is ai visibility tracking just a gimmick?

**AI-drafted labels:** M=Y R=n N=n C=n · expected score 40

**AI note:** category-level discussion


**Sentences naming Kasparro/Kaspr:**
> AI visibility tracking is not inherently a gimmick, but it is currently more of a "directional indicator" than a precise science, making tools like Kasparro and its competitors useful for identifying trends rather than guaranteed ROI .

Full answer: response_id `b7768287-1be1-4089-bbbd-c0908289b0b9` in the console or the pack.

Decision: ☐ keep ☐ change → ________

## 5. H2-005-chatgpt (holdout2, chatgpt)

**Q:** does kasparro actually work or is ai visibility tracking just a gimmick?

**AI-drafted labels:** M=Y R=n N=Y C=n · ambiguous: negative · expected score 30

**AI note:** evidence doubt about Kasparro's claims (rubric c)

- evidence for negative: "Those are internal statistics published by Kasparro rather than independently validated results."

**Sentences naming Kasparro/Kaspr:**
> Short answer: **AI visibility tracking is a real problem, but many tools oversell how precisely they can measure it.** Kasparro falls into a category of tools trying to solve a legitimate need, but I'd be skeptical of taking any single "AI visibility score" at face value.
> ### Looking specifically at Kasparro
> From its public site, Kasparro claims to:
> 
> Those are internal statistics published by Kasparro rather than independently validated results.
> … 2 more in the full answer

Full answer: response_id `08f81acc-0824-4e3a-a5d5-58446e2a6a90` in the console or the pack.

Decision: ☐ keep ☐ change → ________

## 6. H2-005-gemini (holdout2, gemini)

**Q:** does kasparro actually work or is ai visibility tracking just a gimmick?

**AI-drafted labels:** M=Y R=n N=n C=n · expected score 40

**AI note:** doubt about the whole category, not Kasparro


**Sentences naming Kasparro/Kaspr:**
> To understand whether platforms like Kasparro (or similar AI tracking tools) actually work, it helps to look at what they can genuinely do versus the inherent limitations of the technology.
> If you are considering using Kasparro or a similar tool, keep these ground rules in mind:

Full answer: response_id `44a32b81-7166-44dc-bac3-8cd2ae40da73` in the console or the pack.

Decision: ☐ keep ☐ change → ________

## 7. H2-006-aimode (holdout2, aimode)

**Q:** does kasparro track brand visibility on both chatgpt and copilot?

**AI-drafted labels:** M=Y R=n N=n C=Y · ambiguous: entity_confusion · expected score 20

**AI note:** C1-like: cannot tell what Kasparro is

- evidence for entity_confusion: "are you asking about a specific tool named "Kasparro," or were you asking in general about AI brand visibility tools?"

**Sentences naming Kasparro/Kaspr:**
> To provide a more specific answer, are you asking about a specific tool named "Kasparro," or were you asking in general about AI brand visibility tools?

Full answer: response_id `8f761923-2485-4a8f-817a-563bc1396fbf` in the console or the pack.

Decision: ☐ keep ☐ change → ________

## 8. H2-006-chatgpt (holdout2, chatgpt)

**Q:** does kasparro track brand visibility on both chatgpt and copilot?

**AI-drafted labels:** M=Y R=n N=Y C=n · ambiguous: negative · expected score 10

**AI note:** capability not publicly confirmed (rubric c)

- evidence for negative: "not yet—at least not publicly for Copilot."

**Sentences naming Kasparro/Kaspr:**
> Based on Kasparro's current public positioning, **not yet—at least not publicly for Copilot.**
> Kasparro consistently describes itself as an AI visibility platform focused on helping brands be discovered in major AI assistants.
> 
> I couldn't find any public documentation stating that Kasparro currently tracks **Microsoft Copilot**.
> 
> … 1 more in the full answer

Full answer: response_id `fa0dff8e-b96c-49b0-bcf3-0d410451bdf4` in the console or the pack.

Decision: ☐ keep ☐ change → ________

## 9. H2-006-gemini (holdout2, gemini)

**Q:** does kasparro track brand visibility on both chatgpt and copilot?

**AI-drafted labels:** M=Y R=n N=n C=n · expected score 40

**AI note:** affirmative factual answer


**Sentences naming Kasparro/Kaspr:**
> **Yes**, Kasparro tracks brand visibility, representation, and recommendations across major LLMs and AI search engines, **including ChatGPT**.
> However, looking at their core platform architecture and multi-engine tracking scope, their primary focus across major product updates centers heavily on primary generative engines like **ChatGPT, Claude, Gemini, Perplexity, and Google AI**. Microsoft Copilot (while operating ...
> ### Key Capabilities of Kasparro's AI Visibility Platform:
> * **Multi-Engine Audits:** Evaluates how brands are discovered, recommended, and structured inside AI-driven discovery.
> * **Scoring & Discovery:** Measures brand presence across dimensions like search visibility, trust signals, and content quality.

Full answer: response_id `9630ab41-2e94-4cfc-b22f-478264263a56` in the console or the pack.

Decision: ☐ keep ☐ change → ________

## 10. H2-008-gemini (holdout2, gemini)

**Q:** how does kasparro's audit system compare to otterly ai's features?

**AI-drafted labels:** M=Y R=n N=n C=n · expected score 40

**AI note:** refusal


**Sentences naming Kasparro/Kaspr:**
> I am unable to provide comparisons or information regarding Kasparro's audit system or Otterly AI's features.

Full answer: response_id `6b68f8f8-5ecd-466c-9664-801227a9167c` in the console or the pack.

Decision: ☐ keep ☐ change → ________

## 11. D-010-aimode (dev, aimode)

**Q:** is kasparro missing any major ai search engines like Gemini or Claude?

**AI-drafted labels:** M=Y R=n N=Y C=n · expected score 10

**AI note:** states a capability gap (rubric a)

- evidence for negative: "Kasparro appears to be missing major AI models like Anthropic's Claude and Google's Gemini"

**Sentences naming Kasparro/Kaspr:**
> Based on the provided search results from early 2026, **Kasparro appears to be missing major AI models like Anthropic's Claude and Google's Gemini** , which are currently recognized as top-tier competitors alongside ChatGPT.
> - **Find if there are any updates** regarding new integrations for Kasparro?

Full answer: response_id `95f393e4-e371-4acf-8c6e-1a74bf65c045` in the console or the pack.

Decision: ☐ keep ☐ change → ________

## 12. D-010-chatgpt (dev, chatgpt)

**Q:** is kasparro missing any major ai search engines like Gemini or Claude?

**AI-drafted labels:** M=Y R=n N=n C=n · ambiguous: negative · expected score 40

**AI note:** gap stated only conditionally ('if they're not already included')


**Sentences naming Kasparro/Kaspr:**
> If you're positioning **Kasparro** as an AI search/discovery platform, then yes—I'd consider these major omissions if they're not already included:
> If Kasparro aims to be comprehensive, I'd also expect support for or tracking of:
> If Kasparro currently tracks only ChatGPT, Perplexity, Copilot, or a subset of these, then **Gemini and Claude are significant gaps** because they represent a substantial share of AI-assisted search and research workflows.
> If you can share Kasparro's current list of supported engines, I can point out exactly what's missing.

Full answer: response_id `9074ca1a-a68c-4c1d-9473-e0e9748eda2e` in the console or the pack.

Decision: ☐ keep ☐ change → ________

## 13. D-010-gemini (dev, gemini)

**Q:** is kasparro missing any major ai search engines like Gemini or Claude?

**AI-drafted labels:** M=Y R=n N=n C=n · expected score 40

**AI note:** affirmative factual capability answer, not a recommendation


**Sentences naming Kasparro/Kaspr:**
> No, **Kasparro** (an AI visibility and brand intelligence platform) is **not missing** major AI search engines like Gemini or Claude.
> Official product documentation, engineering specifications, and company positioning confirm that Kasparro actively monitors, audits, and measures brand representation across **both Gemini and Claude**, alongside other major AI engines like ChatGPT, Perplexity, and Google AI Mode.

Full answer: response_id `95a7db89-bcd6-49fa-bd03-ab098605fcc1` in the console or the pack.

Decision: ☐ keep ☐ change → ________

## 14. H2-012-aimode (holdout2, aimode)

**Q:** what do real enterprise users say about kasparro's ai revenue diagnostic?

**AI-drafted labels:** M=Y R=n N=Y C=n · ambiguous: negative · expected score 30

**AI note:** no reviews found (rubric c), consistent with H02

- evidence for negative: "there are no specific, publicly available testimonials or reviews from enterprise users regarding"

**Sentences naming Kasparro/Kaspr:**
> Based on the provided search results, there are no specific, publicly available testimonials or reviews from enterprise users regarding **Kasparro's AI revenue diagnostic** tool.
> However, based on the product description provided by Kasparro as of July 2026, the tool is designed for **seller-side revenue infrastructure** and targets specific, actionable results.
> - **Actionable Deliverables:** Kasparro promises a diagnostic report in 14 days, covering five surfaces (e.g., e-commerce, sales channels) and the top 500 SKUs.
> - **No-Frills Setup:** The company emphasizes a direct approach with no retainer or setup fees.
> While specific feedback on Kasparro is not in the search results, general enterprise sentiment in early 2026 shows that companies are moving away from "AI hype" and looking for tools that directly impact P&L by reducing costs or increasing revenue.
> … 1 more in the full answer

Full answer: response_id `05bdabb0-f779-42bd-9a31-f33b53274e32` in the console or the pack.

Decision: ☐ keep ☐ change → ________

## 15. H2-012-chatgpt (holdout2, chatgpt)

**Q:** what do real enterprise users say about kasparro's ai revenue diagnostic?

**AI-drafted labels:** M=Y R=n N=Y C=n · ambiguous: negative · expected score 10

**AI note:** no independent reviews (rubric c)

- evidence for negative: "I couldn't find evidence of a substantial body of independent enterprise user reviews specifically about"

**Sentences naming Kasparro/Kaspr:**
> I couldn't find evidence of a substantial body of independent enterprise user reviews specifically about **Kasparro's AI Revenue Diagnostic**.
> - Kasparro has an online presence describing its AI visibility and brand engineering services, and recent hiring posts explain that its engagements begin with a diagnostic.
> 
> Instead of relying on testimonials, I'd ask Kasparro for:

Full answer: response_id `d5043498-a516-463e-b97b-5fc917f5e26a` in the console or the pack.

Decision: ☐ keep ☐ change → ________

## 16. D-017-chatgpt (dev, chatgpt)

**Q:** is kasparro worth the money compared to peec ai?

**AI-drafted labels:** M=Y R=n N=Y C=n · expected score 10

**AI note:** unfavourable comparison with a named competitor (rubric b)

- evidence for negative: "For most small teams, I'd choose Peec AI over Kasparro."

**Sentences naming Kasparro/Kaspr:**
> Assuming you mean **Kasparro** (the AI visibility/GEO platform, not Kaspr for sales prospecting), my answer is:
> **For most small teams, I'd choose Peec AI over Kasparro.**
> Category | Peec AI | Kasparro
> ### When Kasparro is worth it
> Kasparro makes more sense if you want:
> … 1 more in the full answer

Full answer: response_id `c3b978b0-d181-4941-8d88-241cab857499` in the console or the pack.

Decision: ☐ keep ☐ change → ________

## 17. D-017-gemini (dev, gemini)

**Q:** is kasparro worth the money compared to peec ai?

**AI-drafted labels:** M=Y R=n N=n C=Y · expected score 20

**AI note:** C2: describes Kasparro as the Kaspr prospecting tool; 'Buy Kasparro if' is about that entity (R-I3)

- evidence for entity_confusion: "Comparing Kasparro (often searched or spelled as Kaspr) and Peec AI"

**Sentences naming Kasparro/Kaspr:**
> Comparing **Kasparro** (often searched or spelled as *Kaspr*) and **Peec AI** is a classic "apples to oranges" dilemma because they serve completely different parts of the business funnel:
> * **Kasparro / Kaspr:** A **sales intelligence and B2B prospecting tool** used to find phone numbers, emails, and LinkedIn contact data.
> | Feature Category | Kasparro (Kaspr) | Peec AI |
> Buy Kasparro if:
> * You spend a lot of time on LinkedIn Sales Navigator and need a tool to pull verified direct dials and email addresses cleanly.

Full answer: response_id `b064461f-7855-477d-bded-95dbb6e9562c` in the console or the pack.

Decision: ☐ keep ☐ change → ________

## 18. H2-018-aimode (holdout2, aimode)

**Q:** is kasparro overpriced for B2B SaaS startups?

**AI-drafted labels:** M=Y R=n N=n C=n · expected score 40

**AI note:** generic SaaS pricing discussion


**Sentences naming Kasparro/Kaspr:**
> Based on the current landscape, determining if **Kasparro** (or any similar specialized B2B SaaS tool) is "overpriced" depends entirely on its ability to drive revenue, reduce operational costs, or provide measurable efficiency for a startup.
> - **The Verdict:** If Kasparro provides a 10x ROI (e.g., saves hours of manual work or brings in high-value clients), it is likely not overpriced, regardless of its sticker price.
> The key is whether Kasparro provides true AI efficiency or is merely "lipstick on the pig," notes a .
> - **Operational Leverage:** If Kasparro reduces headcount needed or automates crucial processes (sales, marketing, customer success), it's likely a high-leverage tool.
> - **Comparison:** If Kasparro costs similar to industry competitors (e.g., Salesforce, HubSpot, or specialized vertical SaaS), it is likely priced according to market standards.
> … 2 more in the full answer

Full answer: response_id `6ba5d428-1b45-4c6d-9263-73129d059b01` in the console or the pack.

Decision: ☐ keep ☐ change → ________

## 19. H2-018-chatgpt (holdout2, chatgpt)

**Q:** is kasparro overpriced for B2B SaaS startups?

**AI-drafted labels:** M=Y R=n N=n C=Y · expected score 20

**AI note:** C2: describes Kasparro as an outbound agency

- evidence for entity_confusion: "the B2B SaaS growth/outbound agency, not Kaspr"

**Sentences naming Kasparro/Kaspr:**
> If you mean **Kasparro** (the B2B SaaS growth/outbound agency, not Kaspr), I couldn't find reliable public pricing or enough verified information to judge whether it's objectively overpriced.
> - **Scope.** If Kasparro is only booking meetings, the price should generally be lower than if they're handling strategy, ICP refinement, messaging, infrastructure, multichannel campaigns, and optimization.

Full answer: response_id `1d2dc007-0757-480d-a086-6b6e2e13c463` in the console or the pack.

Decision: ☐ keep ☐ change → ________

## 20. H2-018-gemini (holdout2, gemini)

**Q:** is kasparro overpriced for B2B SaaS startups?

**AI-drafted labels:** M=Y R=n N=n C=n · expected score 40

**AI note:** conditional ROI discussion


**Sentences naming Kasparro/Kaspr:**
> Whether Kasparro is "overpriced" for a B2B SaaS startup depends entirely on how you view **AI Engine Optimization (AEO)** and brand visibility within LLMs (like ChatGPT, Claude, and Perplexity) relative to your current growth stage and budget.
> Kasparro builds an **AI Visibility platform** designed to help companies understand and optimize how they are represented across generative AI tools—a critical and emerging category as buyers increasingly use AI instead of traditional search engines for product discovery.
> *Are you currently evaluating Kasparro for an early-stage team trying to build initial traction, or for a scaling startup looking to dominate AI search results?*

Full answer: response_id `20958c20-9648-4b12-bbb6-efbbff33d0fe` in the console or the pack.

Decision: ☐ keep ☐ change → ________

## 21. H2-019-aimode (holdout2, aimode)

**Q:** does kasparro lock you into expensive monthly retainers?

**AI-drafted labels:** M=Y R=n N=n C=Y · ambiguous: entity_confusion · expected score 20

**AI note:** C1-like: asks what Kasparro is

- evidence for entity_confusion: "could you please clarify if "Kasparro" is a"

**Sentences naming Kasparro/Kaspr:**
> Based on the provided search results, there is no direct evidence that a company specifically named "Kasparro" locks clients into expensive monthly retainers.
> To provide a more accurate answer, could you please clarify if "Kasparro" is a **software platform** , a **marketing agency** , or a **consultancy**?

Full answer: response_id `51366d92-2978-4654-b6fb-1f5dca180980` in the console or the pack.

Decision: ☐ keep ☐ change → ________

## 22. H2-019-chatgpt (holdout2, chatgpt)

**Q:** does kasparro lock you into expensive monthly retainers?

**AI-drafted labels:** M=Y R=n N=n C=Y · expected score 20

**AI note:** C1: asks which Kasparro; answers about Kaspr

- evidence for entity_confusion: "Could you clarify which Kasparro you mean?"

**Sentences naming Kasparro/Kaspr:**
> If you're referring to **Kasparro** (rather than Kaspr), I couldn't verify that it has a standard pricing model or a policy that locks customers into expensive monthly retainers.
> If you meant **Kaspr** (the B2B lead generation platform), it does **not** lock users into long-term retainers.
> 
> Could you clarify which **Kasparro** you mean?

Full answer: response_id `953e6675-8bec-4fe1-b53a-2fbcc9df00de` in the console or the pack.

Decision: ☐ keep ☐ change → ________

## 23. H2-019-gemini (holdout2, gemini)

**Q:** does kasparro lock you into expensive monthly retainers?

**AI-drafted labels:** M=Y R=n N=n C=n · expected score 40

**AI note:** favourable factual answer (no lock-in), not a recommendation


**Sentences naming Kasparro/Kaspr:**
> Kasparro is not a traditional marketing or SEO agency that locks clients into rigid, lengthy retainers.
> Instead, it functions as an **AI-native brand intelligence and visibility platform**.
> Key details regarding Kasparro's business and commercial model include:
> * **Platform & Audit-Led Model:** Kasparro focuses on multi-module AI visibility audits and optimization infrastructure.
> Their engagements center around diagnostic-led software analysis (measuring how brands appear in AI engines like ChatGPT, Claude, Perplexity, and Gemini) rather than open-ended human-hour retainers.
> … 2 more in the full answer

Full answer: response_id `b87e2b44-032c-40d8-92e5-a8223212d3d4` in the console or the pack.

Decision: ☐ keep ☐ change → ________

## 24. H2-020-aimode (holdout2, aimode)

**Q:** how long does setup take for kasparro's ai revenue audit?

**AI-drafted labels:** M=Y R=n N=n C=n · expected score 60

**AI note:** factual timeline


**Sentences naming Kasparro/Kaspr:**
> According to methodology, their AI Revenue Diagnostic is designed to be completed within 14 days, with a focus on quick actionability rather than long, drawn-out setup times.
> - **Output:** The deliverable is a per-surface remediation plan.
> The service is focused on seller-side revenue infrastructure for AI-mediated commerce.

Full answer: response_id `4933e11e-0697-4246-bdda-45a160528a2a` in the console or the pack.

Decision: ☐ keep ☐ change → ________

## 25. H2-020-chatgpt (holdout2, chatgpt)

**Q:** how long does setup take for kasparro's ai revenue audit?

**AI-drafted labels:** M=Y R=n N=n C=n · expected score 40

**AI note:** could not verify a fact; no judgment


**Sentences naming Kasparro/Kaspr:**
> I couldn't find a public page for a product specifically called **Kasparro's AI Revenue Audit**, so I can't verify an official setup time.
> If you're referring to Kasparro's audit service, the setup is typically described as lightweight: you provide access to the relevant business information (such as your website, CRM, analytics, or sales data), complete an intake questionnaire, and then the audit begins.
> If you meant a specific Kasparro offering, could you share either:

Full answer: response_id `9aefbc5a-d270-42d8-b07f-1945b2e98c76` in the console or the pack.

Decision: ☐ keep ☐ change → ________

## 26. H2-020-gemini (holdout2, gemini)

**Q:** how long does setup take for kasparro's ai revenue audit?

**AI-drafted labels:** M=Y R=n N=n C=n · expected score 40

**AI note:** factual description


**Sentences naming Kasparro/Kaspr:**
> Kasparro specializes as an **AI visibility and discovery platform** (scoring brands on how they are seen, recommended, and cited by AI engines like ChatGPT, Gemini, and Perplexity) rather than a traditional financial "revenue audit" tool.
> Because Kasparro's evaluations and diagnostic-led demos focus on AI search presence, brand sentiment, and share of voice, initial visibility audits are typically designed to be rapid and diagnostic-driven—often delivered as part of their initial sales and onboarding consultati...

Full answer: response_id `66854c1c-447b-4eae-9601-d1a5895285e2` in the console or the pack.

Decision: ☐ keep ☐ change → ________

## 27. H2-021-chatgpt (holdout2, chatgpt)

**Q:** is onboarding with kasparro faster than dageno ai?

**AI-drafted labels:** M=Y R=n N=n C=n · ambiguous: negative · expected score 40

**AI note:** no documented onboarding found; mostly a missing fact


**Sentences naming Kasparro/Kaspr:**
> Based on publicly available information, **Kasparro does not appear to have a documented onboarding process that can be directly compared with Dageno AI**, so it's not possible to say definitively that it's faster.
> - I couldn't find a reliable source that states **Kasparro's average onboarding time**, setup flow, or implementation timeline.
> | Factor | Dageno AI | Kasparro |
> If you meant a specific **Kasparro** product (or can share its website), I can compare the two in more detail, including:

Full answer: response_id `9ef923c0-987a-4df8-96f4-6072f6bf16ee` in the console or the pack.

Decision: ☐ keep ☐ change → ________

## 28. H2-021-gemini (holdout2, gemini)

**Q:** is onboarding with kasparro faster than dageno ai?

**AI-drafted labels:** M=Y R=n N=n C=n · expected score 40

**AI note:** no benchmark; neutral


**Sentences naming Kasparro/Kaspr:**
> When comparing onboarding speeds for **Kasparro** and **Dageno AI** (both operating in the Generative Engine Optimization / AI brand intelligence space), there are no official, standardized benchmarks or public metrics directly measuring their time-to-value or setup velocity.
> Enterprise Setup:** Dageno AI offers structured self-serve tiers (starting from basic project setups with predefined prompt limits up to enterprise plans with dedicated onboarding). Kasparro operates similarly as an AI-native brand intelligence and audit platform, where initia...

Full answer: response_id `da579a76-82ed-4c77-927d-6af8329d0a3e` in the console or the pack.

Decision: ☐ keep ☐ change → ________

## 29. D-025-aimode (dev, aimode)

**Q:** is kasparro available for self serve or do you have to talk to sales?

**AI-drafted labels:** M=Y R=n N=n C=n · expected score 40

**AI note:** factual: sales-led, from job postings


**Sentences naming Kasparro/Kaspr:**
> Based on recent job postings for **Kasparro AI** , they operate with a dedicated sales team rather than a pure self-serve model.
> - **Sales-Assisted Focus:** Job descriptions for **Sales Development Representatives** (July 2026) indicate that they actively prospect, conduct outreach, and handle conversations, suggesting a sales-led approach.
> - **SDR Role:** Sales Development Representatives are tasked with making 20-30 calls a day to potential customers to introduce the platform, indicating this is not a fully self-serve product.
> Therefore, you will most likely **have to talk to sales** or a representative to get started with Kasparro.

Full answer: response_id `ffdd37a9-6c48-4dff-8abd-c455bc9580b2` in the console or the pack.

Decision: ☐ keep ☐ change → ________

## 30. D-025-chatgpt (dev, chatgpt)

**Q:** is kasparro available for self serve or do you have to talk to sales?

**AI-drafted labels:** M=Y R=n N=n C=Y · ambiguous: negative · expected score 20

**AI note:** C1: answers about Kaspr; 'couldn't identify a well-known SaaS by that exact name' borderline (c)

- evidence for entity_confusion: "If you mean Kaspr (the LinkedIn prospecting tool), it's available as self-serve for most customers."

**Sentences naming Kasparro/Kaspr:**
> If you mean **Kaspr** (the LinkedIn prospecting tool), it's available as **self-serve** for most customers.
> 
> - Enterprise onboarding and compliance features
> If you meant **Kasparro** (a different product/company), let me know which one you mean—I couldn't identify a well-known SaaS by that exact name.

Full answer: response_id `42e35106-67bf-48c8-aaca-4e8ccf910e77` in the console or the pack.

Decision: ☐ keep ☐ change → ________

## 31. D-025-gemini (dev, gemini)

**Q:** is kasparro available for self serve or do you have to talk to sales?

**AI-drafted labels:** M=n R=n N=n C=Y · expected score 0

**AI note:** C1: only Kaspr, Kasparro never named

- evidence for entity_confusion: "Kaspr is primarily available as a self-serve platform."

**Sentences naming Kasparro/Kaspr:**
> Kaspr is primarily available as a **self-serve platform**.
> * **Self-Serve:** You can sign up directly on their website, install their Chrome extension, and choose from their standard or freemium self-serve plans using a credit card without ever speaking to sales.
> * **When you have to talk to sales:** You only need to contact the sales team if you are looking for custom, high-volume, or enterprise-grade packages (often managed alongside Cognism, its parent company).

Full answer: response_id `136b8240-008c-46ff-b744-592c4d859e98` in the console or the pack.

Decision: ☐ keep ☐ change → ________

## Appendix: model disagreement (read after deciding)

Cases where classify-v1 or classify-v2 disagreed with the AI-drafted label in the fresh-v2 comparison. Disagreement does not mean the label is wrong.

| Case | Label | AI-drafted | classify-v1 | classify-v2 |
|---|---|---|---|---|
| D-004-aimode | negative | n | Y | n |
| D-004-gemini | recommended | n | Y | n |
| H2-005-aimode | recommended | n | Y | n |
| H2-005-aimode | negative | n | Y | Y |
| H2-005-chatgpt | recommended | n | Y | n |
| H2-005-gemini | recommended | n | Y | n |
| H2-005-gemini | negative | n | Y | n |
| H2-006-aimode | entity_confusion | Y | n | n |
| H2-006-chatgpt | recommended | n | Y | n |
| H2-006-chatgpt | negative | Y | Y | n |
| H2-006-gemini | recommended | n | Y | Y |
| D-010-chatgpt | negative | n | Y | Y |
| D-010-gemini | recommended | n | Y | n |
| D-017-gemini | recommended | n | Y | n |
| H2-018-chatgpt | negative | n | Y | n |
| H2-018-chatgpt | entity_confusion | Y | n | Y |
| H2-018-gemini | recommended | n | Y | n |
| H2-019-aimode | entity_confusion | Y | n | n |
| H2-019-chatgpt | negative | n | Y | n |
| H2-019-chatgpt | entity_confusion | Y | n | n |
| H2-019-gemini | recommended | n | Y | n |
| H2-020-aimode | recommended | n | Y | n |
| H2-020-gemini | recommended | n | Y | n |
| H2-021-chatgpt | negative | n | Y | Y |
| D-025-chatgpt | negative | n | Y | Y |

Both prompts disagree with the AI-drafted label in 8 places; if time is short, these are the cases worth re-reading first: D-010-chatgpt (negative), D-025-chatgpt (negative), H2-005-aimode (negative), H2-006-aimode (entity_confusion), H2-006-gemini (recommended), H2-019-aimode (entity_confusion), H2-019-chatgpt (entity_confusion), H2-021-chatgpt (negative).

## Decision log template (one line per decided case)

```json
{"case_id": "D-004-aimode", "audit_item": null, "decision": "keep", "changes": {}, "reason": "<why>", "decided_by": "candidate", "basis": "candidate read the answer (FRESH_V2_REVIEW_SHEET.md)", "recorded_at": "<YYYY-MM-DDTHH:MM>"}
{"case_id": "<id>", "audit_item": null, "decision": "change", "changes": {"expected_set": {"negative": true}, "evidence_replace": {"negative": ["<verbatim excerpt from the answer>"]}}, "reason": "<why>", "decided_by": "candidate", "basis": "candidate read the answer (FRESH_V2_REVIEW_SHEET.md)", "recorded_at": "<YYYY-MM-DDTHH:MM>"}
```

A label set to true needs at least one verbatim evidence excerpt, or the build fails. After building fresh-v3, add its hash pin and a `fresh-v3` entry in `evaluation/compare.py` before comparing.
