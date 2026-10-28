# Research notes (28 Oct 2026)

Kept proportional to the time budget. **V** = verified in this session (by reading the supplied pack or by running code), **S** = from the supplied reference material, **A** = assumption or background knowledge not re-verified online in this session.

## Domain
* **S** Inclusion, recommendation, negative characterisation and citation presence are separate observations; a passing reference is not a recommendation; prose has no automatic rank (Brand_and_domain_brief.txt).
* **S** Failed requests must not be treated as observed absence. Report k/valid alongside valid/attempted coverage (the brief's 12 / 2 / 4-of-10 example, now a unit test).
* **S** Google: existing SEO fundamentals apply to AI Overviews/AI Mode; no special AI schema; eligibility ≠ inclusion (https://developers.google.com/search/docs/appearance/ai-features, via `reference/domain_guidance.jsonl`, reviewed 2026-10-27).
* **S** OpenAI: OAI-SearchBot (search) and GPTBot (training) are controlled independently; a crawler setting does not explain one answer (https://developers.openai.com/api/docs/bots).
* **V** Snapshot facts (see PROJECT.md): Kasparro named in 0 of 75 unbranded answers by simple text match; frequent confusion with "Kaspr" (a LinkedIn prospecting tool); many Kasparro-related citations are job listings.
* **V** `reference/brand_snapshot.json` Organization JSON-LD (2026-07-31) has name, url, logo, description, foundingDate 2026, areaServed, knowsAbout, and **no `sameAs`**. This is a company-declared snapshot, not validation.

## Technical
* **V** Ollama structured outputs: passing a JSON schema in `format` constrained `gemma4:12b` to schema-shaped JSON; `think: false` disables the thinking phase; `temperature: 0` and a fixed seed were used. On an RTX 3050 6 GB, about 35–110 s per answer (prompt eval plus about 6 tokens/s generation).
* **V** Constrained decoding guarantees shape, not truth. Tuning showed paraphrased "quotes" (table cells), so exact-quote grounding plus validator-feedback retries were needed (FAILURES.md F3/F4).
* **A** Wilson score intervals behave better than normal-approximation intervals for small n and rates near 0/1, which matters for 0/75-style results.
* **A** SQLite `BEGIN IMMEDIATE` acquires the write lock at transaction start, so read-check-write transitions are serialised; triggers give defence in depth against direct writes.
* **A** FastAPI/Pydantic v2: `extra="forbid"` request models reject unexpected fields (used to refuse caller-supplied `actor`/`role`); OpenAPI docs are generated automatically.

## Evaluation practice
* Keep tuning cases separate from the final check; report per-label precision/recall plus agreement; report ambiguous labels both included and excluded; do not use an LLM to grade its own prose (assignment brief).
* Verify arithmetic independently: hand-computed expected scores vs the scoring module.
* Evidence checks are mechanical (quote exists in the cited response; the response carries the claimed label; the remedy cites its diagnostic's evidence). They cannot judge whether a hypothesis is true.

## Not researched (deliberately)
Competitor product feature comparisons, market sizing, UI design research, and live AI-engine re-checks. None is needed for the assessed outputs, and new observations would have to be kept separate from the historical snapshot.
