# Decision note

AnswerScope: Kasparro AI-visibility snapshot (150 archived answers, captured 31 Jul 2026). This note is about one page. Details are in the linked files.

**Scoring and aggregation.**
- A succeeded answer scores vis-v1 = clamp(40·mentioned + 40·recommended + 20·first-party citation − 30·negative − 20·entity confusion, 0, 100).
- Inclusion and recommendation are the business outcomes. A citation of kasparro.com is weaker support. The penalties stop a harmful mention from counting as a win.
- A failed or skipped answer gets no score. It is excluded from rates and means and reported as coverage, because counting missing data as absence would hide quality problems.
- Results are always split branded vs unbranded: a prompt that already names Kasparro measures something different.
- Results are also split by engine and topic, with Wilson 95% intervals and paired branded/unbranded prompts.
- Known weakness, kept deliberately and disclosed: a confused mention scores 20, which is higher than an absent one (0).

**Backend, review and reliability.**
- Stack: FastAPI + Pydantic (`extra="forbid"`) over SQLite with WAL and `BEGIN IMMEDIATE` transactions.
- The local model (Ollama gemma4:12b, temperature 0, fixed seed, JSON schema) only labels meaning: recommended, negative, entity confusion, competitors.
- Code does everything else:
  - checks every quote verbatim against the source and stores its offsets;
  - rejects a mention flag that disagrees with the text;
  - retries with the validator's feedback (at most 3 attempts);
  - does the counting, scoring, ranking, permissions and state changes.
- Each answer's outcome is committed on its own, so one failure never loses the others.
- Every model call is traced (input SHA-256, raw output, latency). Recordings allow keyless replay, and a replay is refused if its input hash changed.
- Roles come from server-side token configuration.
- Report versions are immutable. A reviewer decides on one version, pinned by the content SHA-256 they read. Export defaults to the latest version and refuses it unless that exact content is approved. An older approval exports only on explicit request and is marked superseded.
- SQLite triggers also block edits to frozen versions and illegal transitions.

**Alternatives rejected.**
- Letting the LLM score or write diagnostics: not auditable, and it would let the model invent evidence.
- A rank-weighted score: list positions are rarely observable.
- A job queue: a bounded synchronous flow is allowed, and the CLI handles long live runs.
- A hosted API: not approved, and it costs money.

**Top remedy.** R1 ⟦title from the approved report⟧.
- It is an investigation, not a fix.
- Validation: re-run the same prompts on the same engines and settings, at least 3 runs, with the metric stated beforehand (baseline ⟦value⟧).
- No causal claim is made from a single snapshot.

**Failure and fix (F4, [FAILURES.md](evaluation/FAILURES.md)).**
- My fix for markdown links in quotes (F3) broke matching for quotes that were cut exactly from the source.
- My own evidence checker caught it: the round-trip check failed.
- I fixed the normaliser and added a property test over all 150 answers.
- F5 then showed that a narrow fix can over-correct. Its regression test caught my first attempt.

**Evaluation.**
- 12 holdout and 2 synthetic cases against a keyword baseline: ⟦headline numbers from EVALUATION.md⟧.
- Labels are frozen as labels-v2 after my adjudication of disputed cases. This includes manual site check MC-01, which found that "Revenue Pulse" is a different company.

**Largest risk.** Label definitions and sample size.
- "Negative" includes hedging about missing evidence.
- Some labels have only 1–2 positives in the holdout.
- There is one annotator: the AI drafted the labels and I adjudicated them.
- Some holdout text was seen during prompt design (logged in [LABEL_AUDIT.md](evaluation/LABEL_AUDIT.md)).
- There is one snapshot per prompt and engine. The metrics are indicative, not a ranking.

**Omitted.**
- Citation-support checking (no cited pages were opened).
- Repeated runs to measure variance.
- Product-misattribution coverage in the prompt (H06 class; not added, to avoid tuning on the holdout).
- Async jobs, multi-reviewer approval, review expiry, and Postgres.

**Questions before release.**
1. Is evidence-gap hedging "negative" for the client?
2. Should a confused mention score below an absent one?
3. Which engines and locales matter most?
4. May remedies include outreach to third-party sites?

**AI assistance.**
- Claude Code drafted most code, prompts, labels and documentation.
- I verified the behaviour through:
  - the test suite;
  - a clean-clone run;
  - the console walkthrough;
  - label adjudication (H01, H02, H03, H06) and MC-01;
  - the final report approval.
- Active time: ⟦minutes⟧ (see [TIME_LOG.md](TIME_LOG.md)).
