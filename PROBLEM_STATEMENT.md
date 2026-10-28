# Problem statement (from the supplied brief, pack v1.0, 27 Oct 2026)

Source of truth: `assignment/Assignment.pdf` and `assignment/reference/Brand_and_domain_brief.txt`. This file restates the requirements with IDs; implementation choices are in PROJECT.md.

**Goal.** A small runnable backend that turns 50 prompts and 150 archived answers (ChatGPT, Gemini, Google AI Mode; India, English; captured 31 July 2026 via DataForSEO) into transparent scores, three evidence-backed diagnostics and three prioritised remedies. A human edits and reviews the report, and the backend controls which version can be exported. The product answers: where does Kasparro appear to win or lose in this snapshot, what evidence supports it, and what should be investigated or changed next.

## Requirements

| ID | Requirement |
|---|---|
| R1 | Account for all 150 responses: structured result, explicit failure, or skipped reason. |
| R2 | Labels (may overlap): absent, mentioned, recommended, negatively characterised. A mention is not a recommendation. |
| R3 | Extract named competitors, recommendation position when observable, supplied citations. |
| R4 | Transparent visibility score: scale, components, weights, uncertainty; keep component values and exact evidence excerpts or locations. A failed analysis is not a zero. |
| R5 | Persist raw inputs, analysis results, report versions, review decisions; sensible module boundaries; health endpoint; API docs or example requests. |
| R6 | Capabilities: import/validate, run/inspect analysis, edit draft, submit immutable version, approve/reject, export approved version. |
| R7 | Validate requests and model outputs; bound timeouts, retries, calls, output sizes; handle empty/malformed output and provider failure without inventing results. |
| R8 | Trace response IDs through status, prompt/model/scoring config and evidence; label live / local-model / replay / stub; secrets in env; `.env.example`. |
| R9 | Source text and prompts are untrusted; cannot change authority, reviewer identity or export permission; one bad record must not erase valid results. |
| R10 | Appropriate HTTP status codes and structured errors; bounded synchronous flow acceptable with limits explained. |
| R11 | Repeated import of the same response is rejected or safely reused, never silently duplicated; explain. |
| R12 | Two server-configured identities (analyst, reviewer); caller-supplied role/actor is not authorisation. |
| R13 | Submit freezes a version; persist draft/submitted/approved/rejected with actor, decision, version, comment, time; export refuses unapproved, rejected and stale content; editing submitted/approved creates a new draft needing review; old approval exports only its own immutable version. |
| R14 | Demonstrate wrong-role denial, rejection blocking export, edit-after-approval needing new review; describe expiry/concurrency as future work. |
| R15 | Evaluation: ≥ 8 manually labelled supplied responses across all engines and several categories, + 2 own edge cases; selection stated; tuning separate from final check. |
| R16 | Versioned expected labels, source evidence, runnable grader; per-label precision/recall or agreement; separately verify score arithmetic; report eligible/succeeded/failed/skipped. |
| R17 | Check that diagnostic claims have supporting evidence and remedies follow; include an unsupported-claim or incorrect-evidence case; explain grader limits. |
| R18 | Rule-based baseline vs approach on the same cases. |
| R19 | One failure, diagnosis, change and regression case; one command reruns evaluation and writes a readable report. |
| R20 | Compare engines and prompt categories with denominators, coverage, errors; same prompts where possible; identify scoring/category versions. |
| R21 | Three diagnostics (pattern, possible explanation, evidence to test it; response IDs and excerpts). Three remedies (problem, evidence, action, benefit, effort, uncertainty, measurable validation). No invented Kasparro facts or promised ranking gains. |
| R22 | Tests: invalid input, duplicate handling, timeout/malformed, wrong reviewer role, rejection blocks export, edit-after-approval. |
| R23 | Submit: private repo/archive, code, schema, dependency versions, `.env.example`, tests, evaluation cases/runner/results, controlled fixture; README with exact commands and example requests; analysis output JSON; ~1-page decision note; actual active time. |
| R24 | Six active hours, no paid accounts; replay allowed with a real-model adapter, labelled as not proving model quality. |
