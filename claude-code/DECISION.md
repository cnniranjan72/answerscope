# Decision record

| # | Decision | Alternatives considered | Why |
|---|---|---|---|
| 1 | Local Ollama `gemma4:12b` as the real model; record its outputs for replay | Hosted API (not approved, costs money); replay/stub only | Allowed by the pack, free, real semantic step; recordings make the run reproducible without the model |
| 2 | LLM does semantic labelling only; code validates and grounds every quote | Let the LLM also score or write diagnostics | Brief requires deterministic arithmetic/permissions; grounding prevents invented evidence |
| 3 | Mention must agree with lexical presence of "Kasparro" | Trust the model's mention flag | Mention is a lexical fact; the model's value is in recommendation/negativity/confusion |
| 4 | Add `entity_confusion` label | Fold into negative | Inspection showed Kaspr confusion as a distinct, actionable pattern; a misidentification is not an opinion |
| 5 | Analyse the answer body; take citations from citations.jsonl | Analyse full answer_text | The appended URL list would turn citations into "mentions"; the two views of one answer must not be double counted |
| 6 | Score vis-v1 additive with penalties, clamped 0–100; failures excluded | Rank-weighted score; treating failures as 0 | Simple to audit and explain; positions are rarely observable; brief forbids failure-as-zero |
| 7 | Always split branded vs unbranded | One combined rate | Being named in the question changes what inclusion means (brief) |
| 8 | Idempotent import keyed by supplied ID + content SHA-256 (reuse identical, reject conflicting) | Reject all repeats; upsert | Re-running an import is safe and visible; silent overwrite would break traceability |
| 9 | Decision bound to content SHA-256 + latest-version check | Version number only | Guarantees the reviewer approved exactly the bytes later exported |
| 10 | DB triggers in addition to service checks | Service checks only | Defence in depth against direct writes; easy to demonstrate |
| 11 | Export defaults to latest and refuses if not approved; older approvals only by explicit version | Export the latest approved version silently | Prevents presenting stale content as current; matches "old approval only for that clearly identified version" |
| 12 | Synchronous analysis; CLI for long live runs | Background job queue | Bounded synchronous flow is allowed; a queue adds infrastructure without assessed benefit |
| 13 | Diagnostics generated from computed patterns, ranked by affected × severity; remedies templated, analyst-editable | LLM-written diagnostics | Claims stay traceable to counts and verified quotes; a reviewer still controls wording |
| 14 | Static console served by FastAPI, vanilla JS | React/SPA build | User asked for a usable interface; no build step and no extra attack surface |
| 15 | Competitor quotes soft, competitor names hard | Reject the whole output for one bad competitor quote | Core labels stay strictly grounded; secondary detail does not discard a valid classification (F3) |
