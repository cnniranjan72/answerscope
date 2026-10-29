# Five-minute demo

Each step shows one assessed property. Commands assume the repo root, the venv active and `.env` set. Everything is keyless (replay); no model is needed.

| Min | Show | Command / action | What to say |
|---|---|---|---|
| 0:00 | It runs and is healthy | `python -m uvicorn app.main:create_app --factory --port 8000`, then open http://localhost:8000/health and `/docs` | "FastAPI + SQLite; OpenAPI docs are generated." |
| 0:30 | Every answer is accounted for | Console → Analyses: `150 eligible · 148 ok · 2 failed` | "The 2 failures are non-verbatim quotes. They are excluded, not scored as zero." |
| 1:00 | Evidence is real | Open report `7d80ca70` → Key findings → D1–D3. Hover a quote for the exact source text. | "Every quote is checked verbatim against the source and stored with offsets; ⚠ marks weak evidence." |
| 1:45 | Review controls export | `python scripts/demo_review_workflow.py` (21 steps) or: analyst submit → reviewer approve → export | "Wrong role 403; rejected or edited-after-approval content can't export; the decision is pinned to the content hash." |
| 2:30 | Export is self-verifying | `outputs/approved_report_export.json`: `content_sha256` + `content_sha256_covers` | "Strip the 4 export-only evidence fields, hash the canonical JSON, and you get the approved hash (tested)." |
| 3:00 | Honest evaluation | `evaluation/results/eval_report.md` (approved) and `compare_report.md` (sprint) | "v1 over-called 'recommended' (precision 0.29). I did not retune on that holdout; I labelled a fresh holdout, froze it, then tested v2 on it." |
| 4:00 | Reproducible | `python -m evaluation.compare --from-predictions evaluation/results/compare_predictions.json` and `python -m pytest -q` | "Metrics recompute from saved predictions; the frozen label files are hash-pinned; the tests need no private data." |
| 4:30 | Safe to ship | `docker build -t answerscope-demo .` (image has no supplied data) | "Public-safe image; tokens from the environment; non-root." |

**If asked for a live change:** see INTERVIEW_PREP.md (private), "Likely live change exercises". Habit: say the change → smallest edit → `python -m pytest -q` → report the result honestly.
