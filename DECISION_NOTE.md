# Decision note

AnswerScope analyses the Kasparro AI-visibility snapshot: 150 archived answers, captured 31 Jul 2026.
- **Submitted result:** report `6edb78b8` v1, classify-v2, approved 29 Oct 2026 ([outputs/approved_report_v2.md](outputs/approved_report_v2.md), [analysis_output_v2.json](outputs/analysis_output_v2.json)).
- **Earlier approved report:** `7d80ca70` (classify-v1) stays approved and unchanged.
- **History and records:** [DECISION_LOG.md](DECISION_LOG.md).

**Scoring and aggregation.**
- The score `vis-v1` (0–100) is 40·mentioned + 40·recommended + 20·kasparro.com cited − 30·negative − 20·entity confusion, clamped to 0–100.
- Inclusion and recommendation are the outcomes. A first-party citation is weaker support. The penalties stop a harmful mention from counting as a win.
- A failed or skipped answer gets no score. It is reported as coverage and excluded from rates, because counting it as absence would hide quality problems.
- Results are split by branded vs unbranded, engine and topic, with Wilson 95% intervals and paired prompts.
- Known weakness, disclosed: a confused mention (20) scores above an absent one (0).

**Backend, review and reliability.**
- Stack: FastAPI and Pydantic (`extra=forbid`) over SQLite, with WAL and `BEGIN IMMEDIATE` transactions.
- **The model labels only the semantic fields.** A local Ollama `gemma4:12b` (temperature 0, fixed seed, JSON schema) sets recommended, negative, entity confusion and competitors.
- **Code does the rest and checks the model:**
  - every quote must appear verbatim and is stored with its offsets;
  - classify-v2's recommendation type must agree with the recommended flag;
  - there are at most 3 attempts per answer;
  - counting, scoring, permissions and state changes are all code.
- **One failure never loses other results:** each outcome is committed on its own.
- **Every call is traced**, with input SHA-256, raw output and latency. Keyless replay refuses a recording whose input hash has changed.
- **Review controls export:**
  - roles come from server-side tokens, not from the caller;
  - versions are immutable, and a decision is pinned to the content hash that was read;
  - export refuses unapproved, rejected and stale versions, and an older approval exports only on explicit request;
  - SQLite triggers back these rules up.

**Alternatives rejected.**
- An LLM writing the score or the diagnostics: not auditable.
- A rank-weighted score: list positions are rarely observable.
- A job queue: a bounded synchronous flow is enough, and the CLI handles long runs.
- A paid hosted model: not approved.

**Top remedy.** R1 addresses D1: Kasparro is named in **0/75 unbranded answers**, against 71/74 branded ones (149/150 analysed; 1 failure excluded).
- It is an investigation: a source-coverage audit of the hosts most cited in unbranded answers, checking whether a factual listing is possible through editorial routes.
- Validation: run the same prompts, engines and settings at least 3 times. The primary metric, fixed in advance, is the unbranded mention rate (baseline 0/75).
- No causal or ranking claim is made from one snapshot.

**Failure and fix.**
- **F4:** my fix for markdown links in quotes (F3) broke matching for quotes cut exactly from the source. The round-trip evidence check caught it. I fixed the normaliser and added a property test over all 150 answers.
- **The original prompt's weakness:** classify-v1 over-called "recommended" (precision 0.29 on the original holdout). classify-v2 adds rule-checked recommendation types. On a fresh holdout of 24 answers, frozen before v2 ran, false positives fell from 10 to 2 and score error from 20.0 to 10.8.
- **F6:** the console download re-serialised numbers and broke the export hash. Exports are now saved byte for byte, with a regression test. All six failures are in [FAILURES.md](evaluation/FAILURES.md).

**Largest risk.** Labels and sample size.
- "Negative" includes hedging about missing evidence. v2's negative precision on that fresh holdout was 3/6, so 23/74 may overstate it.
- Entity confusion was found in only 1 of 4 holdout cases, so 9/74 is a lower bound.
- There is one annotator: the AI drafted the labels and I decided them. 31 of the 36 fresh labels have not been re-read.
- There is one snapshot per prompt and engine.

**Omitted.**
- Citation-support checks: no cited page was opened.
- Repeated runs beyond one stability re-run.
- Semantic detection of product misattribution. Only a price advisory exists (claims-v1).
- Async jobs, multi-reviewer approval, review expiry and Postgres. A 72-hour review deadline flags overdue reviews but never approves.

**Questions before release.**
1. Is evidence-gap hedging "negative" for the client?
2. Should a confused mention score below an absent one?
3. Which engines and locales matter most?
4. May remedies include outreach to third-party sites?

**AI assistance.**
- Claude Code drafted most of the code, prompts, labels and documentation. After my first approval it also carried out the improvement sprint: classify-v2, evaluation tooling, reviewer tools and the v2 report draft.
- I verified the work and decided:
  - label adjudication (19 cases), MC-01 and the fresh-label audit items;
  - promoting classify-v2;
  - both reports, as analyst (edits) and as reviewer (approval).
- **Active time:** about 320 minutes, self-reported. AI-assisted session time and unattended model runs are listed separately in [TIME_LOG.md](TIME_LOG.md).
