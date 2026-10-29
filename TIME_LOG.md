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
| 29 Oct 2026, 06:29 | In progress at the time of this log | Resumed the live run after a low-memory interruption at 91/150; added active-time reporting to analysis output and drafted DECISION_NOTE; recorded the candidate's case-by-case label decisions and built labels-v3 from them. |

## 3. Unattended Model Execution

| Start | End / status | Activity | Accounting |
|---|---|---|---|
| 28 Oct 2026, 22:36 | Interrupted at approximately 00:30 on 29 Oct 2026; resumed at approximately 06:30 | Background local-model run targeting 150 recorded answers. The run reached 91/150 before low system memory interrupted execution. It was resumed using `--only-unrecorded`. | Unattended GPU/model execution. Excluded from candidate active time and not added to the AI-assisted session or candidate active-time total. |

## 4. Outstanding Work Before Submission

- Complete the live run and replay any remaining recorded outputs.
- Run the evaluation against the recorded model outputs.
- Finalize EVALUATION.md with actual results.
- Finalize DECISION_NOTE.md.
- Complete the clean-clone audit.
- Review the generated diagnostics and report as a candidate.
- Approve the final report in the review console.

## 5. Final Approval Record

| Item | Status | Time |
|---|---|---|
| Candidate review of final diagnostics and report | Done, 29 Oct 2026 | ~35 min including approval (self-reported) |
| Final report approval in the console | Approved v1 of report `7d80ca70`, 2026-10-29T02:20:33Z, by the reviewer identity, with comment | included above |
| Final candidate active-time total | ~170 min (est.) | sum of section 1 |

**Accounting rule:** Candidate active time, AI-assisted development session time, and unattended model execution are separate categories. They must not be summed into a single claimed active-work total. All estimated durations must remain explicitly marked as estimates.
