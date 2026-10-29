# Your steps: classify-v2 report review (about 30–45 minutes)

Prepared by the AI assistant. Every action below is yours: the AI has not edited, submitted, approved or exported report `6edb78b8`, and must not. The suggested wording is a starting point; change anything you disagree with. Record what you actually did and when, in the templates at the end.

## 0. Prepare (5 min)

```
cd answerscope
git pull
# stop any running uvicorn (Ctrl+C in its window), then:
python -m uvicorn app.main:create_app --factory --port 8000
```
In a second terminal:
```
python -m app.cli backup-db
```
Check:
- `http://localhost:8000/health` shows `"prompt":"classify-v2"` and `"report_generator":"report-v3"`.
- The backup prints `"integrity_check": "ok"`.

## 1. As analyst: edit and submit (15 min)

Sign in at `http://localhost:8000` with the **analyst** token from `.env`. Open **Report 6edb78b8** (chips: `classify-v2`, `report-v3`). Ignore `1dcbae40` (`report-v2`); it is a superseded, unsubmitted draft.

**Decision A: which quotes to remove.** Click **Edit draft**. Under the D2 evidence list, read each quote and decide.

| Quote | Suggested | Reason you can give |
|---|---|---|
| D2 #3 "Kasparro** is an emerging AI brand intelligence and SEO platform" | Remove | A neutral description, not unfavourable framing. The same kind of quote was removed from v1. |
| D2 #6 "Publicly available enterprise user feedback … is currently limited" | Remove | From H2-012-gemini, which you labelled *not negative* on 29 Oct (fresh_review_log.jsonl). |
| D1 #4 "If you already use modern SEO suites (like Semrush or Google Search Console)" | Your call (keep is defensible) | A conditional clause, but it does name a competitor in an unbranded answer. |

Remedies have no tick boxes: ticking D2 #3 also removes the same quote from R2 (R2 #3).

**Decision B: analyst notes.** Paste this into **Analyst notes**, editing as you see fit:

> 1) Method: labels come from classify-v2, promoted on 29 Oct 2026 after evaluation (EVALUATION.md). On the independent holdout2 set it cut "recommended" false positives from 10 to 2 compared with classify-v1, which produced the approved report 7d80ca70. Rates are therefore not comparable with that report: recommended 12/149 vs 40/148 and negative 23/149 vs 30/148 mainly reflect the method change, not a change in the engines' answers (same 31 Jul 2026 capture); only the recommended change lies outside the 95% intervals (report comparison). 2) Entity confusion (9/74 branded answers) is now the third diagnostic. It remains a lower bound: the classifier does not detect product misattribution (evaluation case H06); a separate advisory (claims-v1) flags 2 Kasparro prices cited only to other sites, which are not counted. 3) The negative count is uncertain: on holdout2, 3 of classify-v2's 6 negative calls matched the human label, so 23/74 may overstate unfavourable framing. Quotes that the human labels treat as neutral or not negative were removed. 4) 1 of 150 answers failed validation (non-verbatim quote) and is excluded from all rates, not scored as zero. 5) A live re-run of 38 labelled cases reproduced every label in at least 37 of 38 cases. All counts come from one historical capture; no causal or ranking claims are made.

Click **Save**. Expect: "Draft v1 saved.", no red evidence-check banner, and no ⚠ flags in Key findings. The ⚠ banner about 2 possible product misattributions is an advisory and stays.

**Decision C: submit.** Click **Submit v1 for review**. The version is now frozen, with a 72-hour review deadline.

## 2. As reviewer: decide (10–15 min)

Sign out, then sign in with the **reviewer** token. Open 6edb78b8.

Checklist (tick each yourself):
1. **Compare with another report**: select 7d80ca70 (default) and click **Compare**.
   - The method changed (prompt, generator) on the same capture.
   - Only *recommended* is bold (40/148 → 12/149).
   - Negative (30 → 23) and entity confusion (8 → 9) are within the intervals.
2. **Key findings** match the scorecard: D1 0/75 unbranded, D2 23/74, D3 9/74. No ⚠ evidence flags remain.
3. Read each remaining quote under Diagnostics. Does it support its diagnostic?
4. The analyst notes disclose the method change, the negative-count uncertainty and the advisory.
5. Remedies: R1 and R2 are investigations, not promised outcomes. R3 is low effort.

**Decision D: approve or reject.** A comment is required.

If you approve, a suggested comment:
> Approved v1. classify-v2 draft; I removed one neutral and one label-inconsistent quote (also from R2) and checked the remaining quotes against their answers. The comparison with the approved v1 report shows the method change explains the lower recommended rate; negative and entity-confusion changes are within uncertainty. The analyst notes disclose the method change, the uncertain negative count (holdout2 precision 3/6) and the misattribution advisory. One historical snapshot; citation support not verified.

If you reject, a suggested comment (then fix as analyst, which creates v2, and resubmit):
> Rejected v1: <what is wrong, e.g. a remaining quote that does not support D2 / notes overstate X>. Fix and resubmit.

## 3. After approval: export and verify (5 min)

In the console, click **Export v1**, then download both **JSON** and **readable report (.md)**. Save them as `outputs/approved_report_v2_export.json` and `outputs/approved_report_v2.md`. Then:
```
python -m app.verify_export outputs/approved_report_v2_export.json --answers assignment/data/responses.jsonl
```
Every line should say PASS.

Do not overwrite `outputs/approved_report_export.json` or `outputs/approved_report.md`: they are the approved v1 record.

## 4. Record what you did (5 min), first person and accurate

**DECISION_NOTE.md**: append under the promotion record, filling the blanks with what actually happened:
> **Review of the classify-v2 report (<date>).** As analyst, I removed <quotes> because <reasons> and submitted 6edb78b8 v1. As reviewer, I <approved/rejected> it: <your comment, short>. Export verified with `app.verify_export` (<n>/<n> quotes located).

**TIME_LOG.md**: add a row with your real start and end times (look at the clock, or the console's `submitted_at` / `decided_at`):
> | <date>, <start> | <end> | Candidate: reviewed the classify-v2 draft as analyst (quote removals, notes, submit) and as reviewer (comparison, checklist, <decision>); exported and verified. | Candidate active time |

Leave the AI-assisted rows as they are: they describe work the assistant did, and the time log is evidence of who did what.

**Commit** (Conventional Commits, no co-author trailer):
```
git add outputs/approved_report_v2_export.json outputs/approved_report_v2.md DECISION_NOTE.md TIME_LOG.md
git commit -m "docs: approved classify-v2 report (6edb78b8 v1), export and review record"
git push
```

## 5. Optional: the 31 unread fresh-v2 labels (20–40 min)

Work through `claude-code/FRESH_V2_REVIEW_SHEET.md`. If time is short, re-read the 8 listed at the end of its appendix first. Put your decisions in a new `evaluation/cases/fresh_review_log_v3.jsonl` (template in the sheet). Then ask the assistant to build fresh-v3 and rerun the comparison.
