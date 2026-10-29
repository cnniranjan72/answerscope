# TIME_LOG.md

## 1. Candidate Active Time

Self-reported by the candidate on 29 October 2026. All estimates are approximate (`~`), not clock readings. No duration has been inferred from session timestamps.

| Date | Active time | Activity |
|---|---:|---|
| 28 Oct 2026 | ~30 min | Read the assignment brief and pack, including the provided instructions and supporting materials. |
| 28–29 Oct 2026 | ~60 min | Reviewed the label audit table and full archived answers; made the 28 October adjudication decisions (H01, H02, H03, scoring and H06) and completed the 19-case review on 29 October. Reading and decision-making are counted once, without double-counting overlap. |
| 28 Oct 2026 | ~20 min | Manually checked revenuepulseai.com and the Wayback capture for MC-01 and documented the findings. |
| 28 Oct 2026 | ~25 min | Walked through the review console on port 8000, including the stub report and approve/export workflow. |
| 29 Oct 2026 | ~35 min | Final review of the diagnostics and report against the cited answers. As analyst: removed 5 weak evidence quotes, replaced the D3 hypothesis and the R3 action, edited the notes, submitted. As reviewer: approved v1 with a comment and exported it. |
| **Total candidate active time** | **~170 min (~2 h 50 min)** | **Verified self-reported entries only.** |

### Candidate time accounting notes

- These durations are candidate-reported estimates, not independently measured timings.
- The label-review estimate combines reading and adjudication to avoid double-counting overlapping work.
- The final diagnostics review and report approval (~35 min, self-reported) are included in the total.
- No active time is claimed for work that has not yet been performed.

## 2. AI-Assisted Development Session

The following are wall-clock intervals recorded during the Claude Code-assisted development session on 28 October 2026. They describe the overall assisted work session, not independently measured candidate-active minutes. They are reported separately from the candidate active-time total.

| Start (IST) | End (IST) | Activity |
|---|---|---|
| 22:07 | 22:13 | Read START_HERE, brief, Assignment.pdf, READ_ME, schema and fixtures; ran the pack checker; profiled data; tested local-model latency. |
| 22:13 | 22:28 | Implemented backend configuration, schema, ingestion, text/citation/category/scoring modules, model adapters, analyzer and prompt v1; ran a tuning probe on five tuning cases and identified F1. |
| 22:28 | 22:36 | Implemented reports, review state machine, API and CLI; ran stub smoke test and identified F2; brought tests from 57 to green; investigated F3 during the initial live run, fixed it and restarted the run. |
| 22:36 | 22:43 | Created labels for 17 supplied cases and two synthetic cases; implemented the evaluation runner and review console; identified and fixed F4 through the evidence checker. |
| 22:43 | 22:49 | Prepared documentation and workflow demo script; ran a secret scan. |
| 23:00 | 23:12 | Audited all 17 supplied cases; revised the rubric, created the audit script and proposed v2 labels; ran tests and recorded candidate adjudication. |
| 23:12 | 23:20 | Checked live-run health, logged the H11 issue, implemented the resume flag, ran a clean-clone check (96 seconds), and drafted EVALUATION and HANDOFF materials. |
| 23:20 | 23:50 | Wrote the MC-01 site-check findings; adjudicated H06; froze labels-v2; fixed F5; checked the console in headless Chrome; fixed the mobile layout; reviewed call statistics; prepared the README reading guide. |
| 29 Oct 2026, 06:29 | 07:55 | Resumed the live run after a low-memory interruption at 91/150; added active-time reporting to analysis output and drafted DECISION_NOTE; recorded the candidate's case-by-case label decisions and built labels-v3 from them; full replay analysis; recorded S01/S02; evaluation run and EVALUATION results; two report fixes (competitor spelling variants, double full stop); console evidence-removal control; report draft and caveats; export hash note; final docs, clean-clone check and archive. |
| 29 Oct 2026, ~08:00 | ~13:50 | Engineering sprint after approval (separate from the approved submission): fresh-v1 label set (AI-drafted, blind, frozen); classify-v2 candidate prompt and rules; evidence-v2 warnings; review deadline; synthetic robustness fixtures; three-way comparison runner and report; stability study; candidate full-pack v2 output; Docker image and CI workflow; documentation; acceptance gate. Timestamps from commit times (first sprint commit 08:05). |
| 29 Oct 2026, ~14:30 | ~17:20 | AI-assisted session, performed autonomously by the AI assistant (no candidate minutes claimed; the candidate's in-session decisions were the fresh-v1 audit items (~14:35) and the instruction to promote classify-v2 and draft its report): AI audit of fresh-v1 and fresh-v2 build; classify-v2 promotion; competitor-count fix (report-v2); `draft-report` CLI and demo seeding; evidence-v3 (report-v3) and the v2 report drafts; label-set overwrite guard; review notes and the fresh-v2 review sheet; Render redeploys. Timestamps from commit times. |
| 29 Oct 2026, ~17:20 | ~19:20 | AI-assisted session continued, performed autonomously by the AI assistant while the candidate was away (no candidate minutes claimed): report comparison (API, CLI, console); offline export verifier; `backup-db`; claims-v1 misattribution advisory and a rejected Kaspr-mention experiment; `/health` versions; readable Markdown export; CHANGELOG; dry run of the planned v2 review on a deleted scratch copy (no real decision recorded); clean-clone checks; Render redeploys. Timestamps from commit times. |

## 3. Unattended Model Execution

| Start | End / status | Activity | Accounting |
|---|---|---|---|
| 28 Oct 2026, 22:36 | Interrupted at approximately 00:30 on 29 Oct 2026; resumed at approximately 06:30; completed 07:23 (150/150 recorded; 59 in the resumed part, all succeeded) | Background local-model run targeting 150 recorded answers. The run reached 91/150 before low system memory interrupted execution. It was resumed using `--only-unrecorded`. | Unattended GPU/model execution. Excluded from candidate active time and not added to the AI-assisted session or candidate active-time total. |
| 29 Oct 2026, ~08:20 | Completed ~13:43 with interruptions (killed twice for low memory, resumed with `--only-unrecorded` / `compare --fill-*`) | Sprint model runs: classify-v2 tuning iterations on dev, comparison recordings, full-pack classify-v2 recording (96 answers in the final resumed part: 95 ok, 1 failed), live stability re-runs for v1 and v2 (38 cases each) | Unattended model execution; same accounting as above. |

## 4. Outstanding Work Before Submission

All items are complete as of 29 Oct 2026:
- Live run (150/150 recorded) and full replay analysis (148 succeeded, 2 failed).
- Evaluation on labels-v3; EVALUATION.md results.
- DECISION_NOTE.md.
- Clean-clone audit (see claude-code/HANDOFF.md).
- Candidate review and approval of the final report (section 5).

Sprint (after approval): the AI-drafted fresh-v1 labels received an AI second-pass audit. On 29 Oct (~14:35) the candidate decided its 4 items by accepting the AI suggestions (`evaluation/cases/fresh_review_log.jsonl`). The candidate did not report time for this, so no candidate active time is claimed for the sprint.

Remaining for the candidate: send the submission (private archive or repository) by the reply route described in START_HERE.

## 5. Final Approval Record

| Item | Status | Time |
|---|---|---|
| Candidate review of final diagnostics and report | Done, 29 Oct 2026 | ~35 min including approval (self-reported) |
| Final report approval in the console | Approved v1 of report `7d80ca70`, 2026-10-29T02:20:33Z, by the reviewer identity, with comment | included above |
| Final candidate active-time total | ~170 min (est.) | sum of section 1 |

**Accounting rule:** Candidate active time, AI-assisted development session time, and unattended model execution are separate categories. They must not be summed into a single claimed active-work total. All estimated durations must remain explicitly marked as estimates.
