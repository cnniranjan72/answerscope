# Manual check MC-01: revenuepulseai.com (H06 adjudication)

| Field | Value |
|---|---|
| Check ID | MC-01 |
| Purpose | Resolve label question D-MISATTR for evaluation case H06 (`bc213889-4850-4ae2-bf8e-af1159ff6f9c`, chatgpt, prompt 016) |
| Performed by | Candidate (manual browser check), 28 Oct 2026 |
| Assisted by | AI coding assistant: a prior read-only fetch of the homepage on 28 Oct 2026, used only to prepare the checklist |
| Scope | Read-only viewing of public pages. No forms, accounts, contact or downloads. |
| Status | **Supplemental observation, kept separate from the historical snapshot (captured 31 Jul 2026).** It does not change any archived answer. |

## Why the check was needed
The archived answer states: "Kasparro's 14-day AI Revenue Diagnostic starts at ₹49,999". Its deliverables include founder/team interviews, pipeline/conversion/pricing analysis and a leadership readout. Both statements carry a single inline source, `https://www.revenuepulseai.com/?utm_source=chatgpt.com`. None of the answer's 12 citations is kasparro.com. The pack alone could not establish whether that source belongs to Kasparro.

## Procedure
1. Opened https://www.revenuepulseai.com/ in a browser (live site, 28 Oct 2026).
2. Checked the Wayback Machine: `https://web.archive.org/web/2026*/revenuepulseai.com`.
3. On each version, looked for: the operating company / brand name, any mention of "Kasparro", the diagnostic offering and its duration, any price (₹49,999), and the listed deliverables.
4. Compared the findings with pack evidence about Kasparro.

## Results

| Item | Live site (28 Oct 2026) | Wayback capture (only capture: **4 Oct 2026**) |
|---|---|---|
| Brand / operator | "Revenue Pulse", "a brand operated by AKS Consulting, a sole proprietorship registered in Ahmedabad, Gujarat"; founder Amit Sharma; "© 2026 AKS Consulting" | Same |
| Mentions Kasparro | **No** | **No** |
| Offering | "Revenue Architecture Diagnostic", ~14 working days from evidence received | Same: "~14 working days from evidence received"; context, commercial data and **management interviews**; six-pillar / 36-control assessment; P1/P2/P3 findings; 90-day action architecture and management readout |
| Price for the diagnostic | Not shown ("scoped after initial consultation") | Not shown (the only price on the page is ₹999 for an unrelated AI toolkit) |
| Target market | Founder-led B2B manufacturing / industrial companies | Same |
| `/pricing` | HTTP 404 | n/a |

No capture from on or before 31 Jul 2026 exists in the Wayback Machine, so the July version of the page and the origin of "₹49,999" could not be checked.

## Comparison with pack evidence about Kasparro
* The same prompt's Google AI Mode answer (`0f7ae466…`) cites kasparro.com and describes the diagnostic as covering "five surfaces, top 500 SKUs, and includes a per-surface remediation plan". It says "the specific dollar cost … is not explicitly listed on their website".
* The Gemini answer to the same prompt found no standalone priced "14-day AI revenue diagnostic".
* The brief and `reference/brand_snapshot.json` describe Kasparro as AI-visibility / AI-commerce infrastructure for brands and catalogs, not B2B sales-process consulting.

## Conclusion and decision
* The cited source belongs to a **different, identifiable organisation** (Revenue Pulse / AKS Consulting, Ahmedabad). It offers a similar ~14-day revenue diagnostic built on management interviews and pipeline analysis, and it does not mention Kasparro in either version checked.
* The attributed deliverables match Revenue Pulse's offering and conflict with the kasparro.com-cited description.
* Both conditions of rubric C3 are met. **Candidate decision (28 Oct 2026): H06 `entity_confusion = true`** (product misattribution); `mentioned` stays true (R-I1). vis-v1 score 40 → 20.
* **Residual uncertainty:** the ₹49,999 figure is unverified on any version checked, and there is no pre-capture-date archive. Nothing found suggests a relationship between Revenue Pulse and Kasparro.
