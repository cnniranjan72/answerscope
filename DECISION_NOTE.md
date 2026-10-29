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

**Top remedy.** R1 addresses D1: Kasparro is named in **0/75 unbranded answers**, against 70/73 branded ones (148/150 analysed; 2 failures excluded). The remedy is a source-coverage audit of the hosts most cited in unbranded answers (reddit, linkedin, youtube, medium…), checking whether a factual listing is possible through legitimate editorial routes.
- It is an investigation, not a fix.
- Validation: re-run the same prompts on the same engines and settings, at least 3 runs, with the metric stated beforehand (primary metric: unbranded mention rate, baseline 0/75).
- No causal claim is made from a single snapshot.

**Failure and fix (F4, [FAILURES.md](evaluation/FAILURES.md)).**
- My fix for markdown links in quotes (F3) broke matching for quotes that were cut exactly from the source.
- My own evidence checker caught it: the round-trip check failed.
- I fixed the normaliser and added a property test over all 150 answers.
- F5 then showed that a narrow fix can over-correct. Its regression test caught my first attempt.

**Evaluation.**
- 12 holdout and 2 synthetic cases, compared with a keyword baseline (F1):
  - negative: model **0.89**, baseline 0.40;
  - entity confusion: model **0.80**, baseline 0.50;
  - the injected instruction (S02) fooled the baseline but not the model;
  - recommended: the model is **worse**, at 0.44 against 0.80 (precision 0.29). It treats favourable descriptions as recommendations.
- I did not retune on the holdout. Instead, the report flags that the branded recommendation count (40/73) is likely an overestimate.
- Labels: AI-drafted, then every one of the 19 cases reviewed and decided by me before the final evaluation (labels-v3; 2 changes, log in `evaluation/cases/candidate_review_log.jsonl`). This includes manual site check MC-01: the site cited for H06's price belongs to a different firm and does not mention Kasparro, so H06 is a *suspected* misattribution; no business relationship is claimed either way.

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
- Active time: candidate ~170 min (self-reported estimate, including the final review and approval), shown separately from the AI-assisted session time and the unattended model run (see [TIME_LOG.md](TIME_LOG.md)).

---

**Addendum: post-submission sprint (29 Oct 2026).** The approved submission above is unchanged (tag `submission-v1`).
- **Failure modes.** The main weakness, over-calling "recommended", was traced to five evidenced failure modes ([IMPROVEMENT_PLAN.md](IMPROVEMENT_PLAN.md)).
- **Candidate prompt.** classify-v2 makes an explicit recommendation-type decision, backed by three deterministic validator rules.
- **Honest test.** Because the original holdout had been inspected, a fresh set was labelled (drafted by the AI assistant, blind to predictions) and frozen before any v2 run. I later decided the 4 items an AI audit raised on it (fresh-v2).
- **Results.** On its 24 independent holdout answers, recommendation false positives fell from 10 to 2 and score error from 20.0 to 10.8. Negative recall dropped from 4/4 to 3/4, entity confusion stayed weak (1 of 4), and an injected instruction still steered v2's output: the validator turned that case into a failure rather than a wrong label.
- **Status.** Promoted to the default on 29 Oct 2026; see the promotion record below.
- **Also added.**
  - Advisory evidence-quality warnings.
  - A review deadline that never auto-approves.
  - A resume that is safe against truncated or stale recordings.
  - A fail-loud comparison runner.
  - A public-safe Docker image and a CI workflow.

**Promotion record: classify-v2 becomes the default (29 Oct 2026).**
- **Decision.** I decided to promote classify-v2 after reading the comparison, the stability re-runs and the fresh-label audit.
- **What changed.**
  - New analyses (CLI, API, console) use classify-v2 (`analyzer.PROMPT_VERSION`); `/health` reports it.
  - classify-v1 stays registered and replayable. The approved report `7d80ca70`, `outputs/analysis_output.json` and `evaluation/results/eval_report.md` are classify-v1 results and are unchanged.
  - `evaluation.run_eval` and the keyword baseline are pinned to the classify-v1 contract, so the evaluation of record still reproduces.
- **Rollback.** `--prompt-version classify-v1` per run, or set `analyzer.PROMPT_VERSION` back. Both recording sets are kept.
- **Report.** The classify-v2 report `6edb78b8` v1 (report generator `report-v3`) is approved; see the review record below. The classify-v1 report `7d80ca70` remains approved and unchanged as the original submission. `1dcbae40` is a superseded draft that was never submitted.
- **Known limits carried over.**
  - Negative precision on holdout2 is 3/6.
  - Entity confusion is weak (1/4).
  - Product misattribution (H06) is not detected.
  - holdout2 has too few true recommendations to measure recall.

**Review record: classify-v2 report `6edb78b8` v1 (29 Oct 2026).** Before acting, I spent about two hours reading the sprint decisions and materials (self-reported; TIME_LOG.md).
- **As analyst** (draft saved 19:23:36 IST, submitted 19:23:40), I removed three evidence quotes:
  - D1 #4, a conditional clause ("If you already use modern SEO suites…");
  - D2 #3, a neutral description of Kasparro, which also removed it from R2;
  - D2 #6, from H2-012-gemini, which I had labelled not negative.
- I added analyst notes disclosing the method change, the uncertain negative count and the misattribution advisory. The draft text, the suggested removals and the suggested notes were prepared by the AI assistant (`claude-code/CANDIDATE_STEPS.md`); the decisions to apply them were mine.
- **As reviewer** (approved 19:24:46 IST), I approved v1 with the comment recorded in the export: the method change explains the lower recommended rate, and the negative and entity-confusion changes are within uncertainty. Content SHA-256 `426350ce…`.
- **Export.** `outputs/approved_report_v2_export.json` verifies (`python -m app.verify_export`: all checks pass, 23/23 quotes located). Readable copy: `outputs/approved_report_v2.md`.
  - The copy I first downloaded from the console failed the hash check. The browser had rewritten numbers such as 1.0 as 1 (failure F6, fixed).
  - The committed export was therefore regenerated on the server from the same approved version.
