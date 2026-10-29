# Time log

Times are IST clock readings taken with `date` during the session on 28 Oct 2026. The work was done with an AI coding assistant (Claude Code); the clock times below are wall-clock for that assisted session. **Candidate: add your own reading, review and verification time below; it counts as active work.**

| Start | End | Activity |
|---|---|---|
| 22:07 | 22:13 | Read START_HERE, brief, Assignment.pdf, READ_ME, schema, fixtures; ran pack checker; profiled data; tested local model latency |
| 22:13 | 22:28 | Backend: config, schema, ingestion, text/citation/category/scoring modules, model adapters, analyzer, prompt v1; tuning probe on 5 tuning cases (found F1) |
| 22:28 | 22:36 | Reports + review state machine, API, CLI; stub smoke run (found F2); tests (57 → green); first live run started, stopped after finding F3; fixed; live run restarted |
| 22:36 | 22:43 | Labelled 17 supplied + 2 synthetic cases; evaluation runner; found F4 via evidence checker; fixed; review console |
| 22:43 | 22:49 | Documentation, workflow demo script, secret scan |
| 23:00 | 23:12 | Label audit: full re-read of 17 cases, rubric-v2, audit script, proposed v2 labels, tests; candidate adjudication recorded |
| 23:12 | 23:20 | Live-run health check (exposed H11, logged), resume flag, clean-clone check (96 s), EVALUATION/HANDOFF drafts |
| 23:20 | 23:50 | MC-01 manual site check write-up, H06 adjudication, labels-v2 freeze, F5 fix, console checks (headless Chrome), mobile layout fix, call statistics, README reading guide |
| 29 Oct 06:29 | (open) | Resumed live run after it was stopped for low memory at 91/150; active-time field in analysis output; DECISION_NOTE draft |
| 22:36 | (running) | Background: full 150-answer local-model run with recording (unattended GPU time, not active work). Stopped by low system memory at 91/150 (≈00:30, 29 Oct); resumed 06:30 with `--only-unrecorded` |

Remaining before submission: final analysis from replay, evaluation on recorded model outputs, EVALUATION.md results, DECISION_NOTE.md, clean-clone audit, and **candidate review of diagnostics and the report approval** (label review done 29 Oct).

## Candidate active time

Self-reported by the candidate on 29 Oct 2026. All four values are estimates (~), not clock readings, and none was inferred from session timestamps.

| Date | Minutes | Activity |
|---|---|---|
| 28 Oct 2026 | ~30 (est.) | Reading the assignment brief and pack |
| 28–29 Oct 2026 | ~60 (est.) | Label review: audit table and full archived answers, the 28 Oct adjudication (H01, H02, H03, scoring, H06), and the 29 Oct case-by-case decisions on all 19 cases (reading and deciding counted once) |
| 28 Oct 2026 | ~20 (est.) | MC-01 manual site check (revenuepulseai.com, live site and Wayback capture) and its findings |
| 28 Oct 2026 | ~25 (est.) | Review console walkthrough on :8000 (stub report, approve and export) |
| pending | – | Final report review and approval in the console |
| **Total so far** | **~135 (est.)** | Candidate active time, verified entries only |

These categories are kept apart and not added together:
- Candidate active time (this table).
- The AI-assisted development session (the clock-time table above): the assistant's working time, which the candidate directed.
- Unattended model execution (the background row above), which is not active work.
