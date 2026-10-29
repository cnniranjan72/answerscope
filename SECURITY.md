# Security and data handling

## Identity and authorisation
* Two identities (analyst, reviewer) are defined only in server environment variables (`ANALYST_TOKEN`, `REVIEWER_TOKEN`, names). Startup refuses missing, short (< 16 chars), identical or placeholder tokens.
* Requests authenticate with `Authorization: Bearer <token>`. Tokens are compared in constant time (`hmac.compare_digest`) and mapped to `(name, role)` on the server.
* Request bodies forbid unknown fields. A caller-supplied `actor`, `role` or header like `X-Role` is rejected or ignored and never grants anything (tested).
* Role matrix: analyst can import, analyse, create/edit reports and submit; reviewer can decide; both can read and export. Export authority comes from approval state, not role.
* The reviewer service re-checks the role (defence in depth). Decisions store the server-derived actor name and role.

## Integrity
* Frozen report versions and decisions are protected by SQLite triggers as well as service logic.
* A decision is bound to the SHA-256 of the exact content reviewed; export re-verifies it.
* State transitions run inside `BEGIN IMMEDIATE` transactions.

## Untrusted content
* Prompts and answers are data. They are wrapped in delimiters and the system prompt tells the model to ignore instructions inside them (synthetic case S02 tests an injection attempt).
* The model only proposes labels and quotes. It cannot affect authorisation, identities, approval, export or arithmetic, and every quote is checked against the source.
* The console renders all answer-derived text with `textContent` (no HTML injection).
* Import never reads a client-supplied path: `/datasets/pack` reads only the server-configured `PACK_DIR`.

## Errors and secrets
* Errors are structured (`{"error": {code, message, details}}`). Unexpected exceptions return a generic 500 and are logged server-side. Tokens never appear in responses, reprs or logs (tested).
* `.env` is git-ignored; `.env.example` has placeholders only. No paid or hosted API keys are used.

## Data
* The supplied pack (`assignment/`) is git-ignored and never modified. Replay files, outputs and evaluation results contain answer excerpts, so the repository must stay private.
* No real website, customer system or engine is contacted; the only network call is to a local Ollama server.
* **Incident (29 Oct 2026):** the GitHub remote was found to be **public** while it held replay recordings, labelled cases and outputs with answer excerpts. No credentials were ever committed (secret scan of all history). The candidate was told immediately and made the repository private. Lesson: check repository visibility before the first push, and keep private data out of any image or deploy (see below).
* **Public-safe demo image:** `Dockerfile` + `.dockerignore` ship code, prompts and the synthetic mini fixture pack only. Supplied pack, recordings, outputs, evaluation data, databases and `.env` are excluded; the container runs as a non-root user; tokens come from the environment. Verified by building the image and listing its contents.

## Not implemented (future work)
Token rotation/expiry, rate limiting, TLS (run behind a reverse proxy), audit-log export, escalation routing for overdue reviews (the deadline flag itself is implemented and never auto-approves), and multi-reviewer quorum.
