# AnswerScope

A small FastAPI + SQLite backend that analyses the Kasparro assignment pack: 50 prompts and 150 archived answers from ChatGPT, Gemini and Google AI Mode, captured 31 July 2026. For every answer it records a structured result, an explicit failure, or a skip with its reason. It computes a transparent visibility score, drafts three evidence-backed diagnostics with three remedies, and enforces analyst → reviewer approval before anything can be exported.

* **Semantic step (LLM):** a local model (Ollama `gemma4:12b`) classifies each answer: mentioned / recommended / negative / entity confusion, competitors, list position, with exact quotes. Code validates every output and checks every quote against the source text.
* **Deterministic code:** validation, citation counting, scoring, aggregation, diagnostics ranking, permissions and state transitions.
* **Keyless replay:** the real local-model run is recorded under `replay/classify_v1/`. Replay re-validates those recorded outputs with current code, so the whole workflow runs without a model. Outputs and traces carry their execution mode (`local_model`, `replay`, `stub`).

## Reviewer reading guide (15 minutes)

| Read | For |
|---|---|
| [DECISION_NOTE.md](DECISION_NOTE.md) | One page: scoring, design and review choices, top remedy, failure/fix, risks, AI assistance |
| [outputs/analysis_output.json](outputs/analysis_output.json) and [outputs/approved_report_export.json](outputs/approved_report_export.json) | Scores, coverage, three diagnostics and three remedies; the reviewer-approved export |
| [EVALUATION.md](EVALUATION.md) and [evaluation/results/eval_report.md](evaluation/results/eval_report.md) | Baseline vs model on labelled cases; evidence checks |
| [evaluation/FAILURES.md](evaluation/FAILURES.md) | Five real failures, their diagnoses, fixes and regression tests |
| [outputs/review_workflow_demo.md](outputs/review_workflow_demo.md) | Wrong-role denial, rejection blocking export, edit-after-approval, step by step |
| [IMPROVEMENT_PLAN.md](IMPROVEMENT_PLAN.md) and [evaluation/results/compare_report.md](evaluation/results/compare_report.md) | Post-submission sprint: evidenced failure modes, candidate prompt classify-v2, fresh holdout, three-way comparison |
| [outputs/candidate_v2/](outputs/candidate_v2/README.md) | Full-pack classify-v2 output (candidate, **not approved**); the approved deliverable remains `outputs/approved_report_export.json` |

Supporting detail: [ARCHITECTURE.md](ARCHITECTURE.md), [SECURITY.md](SECURITY.md), [TESTING.md](TESTING.md), [evaluation/LABEL_AUDIT.md](evaluation/LABEL_AUDIT.md), [evaluation/RUBRIC.md](evaluation/RUBRIC.md). Planning records live in `claude-code/` and PROJECT.md / PROBLEM_STATEMENT.md / RESEARCH.md.

## Prerequisites

* Python 3.10+ (tested with 3.12.10 on Windows 11).
* The extracted assignment pack, unchanged, at `./assignment` (or set `PACK_DIR`). It is not in version control.
* Optional, only for live model runs: [Ollama](https://ollama.com) with `ollama pull gemma4:12b`. This is an approximately 8 GB download. On the development laptop (RTX 3050 6 GB) one answer takes about 1–2 minutes, and all 150 take about 4–5 hours. Replay mode needs none of this.

## Setup (under 10 minutes, no model needed)

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate      macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # then replace both tokens with random values:
python -c "import secrets; print(secrets.token_urlsafe(24))"

py -3 assignment/tools/check_pack.py    # (python3 on macOS/Linux) verifies the untouched pack
python -m app.cli init-db               # creates var/answerscope.db from app/db/schema.sql
```

## Run

```bash
python -m uvicorn app.main:create_app --factory --port 8000
```

* Review console: http://localhost:8000/ (sign in with the analyst or reviewer token)
* OpenAPI docs: http://localhost:8000/docs
* Health: `GET /health`

## Tests and evaluation

```bash
python -m pytest -q                      # engineering tests (synthetic fixture + deterministic stub)
python -m evaluation.run_eval            # labelled evaluation, baseline vs model (replay), writes
                                         # evaluation/results/eval_report.md and eval_results.json
python -m evaluation.run_eval --provider ollama   # same cases against the live local model
python -m evaluation.candidate_review            # rebuild labels_v3 from labels_v2 + the candidate's decision log

# Sprint (29 Oct): baseline vs classify-v1 vs classify-v2 (default since 29 Oct), keyless from recordings
python -m evaluation.compare                     # tuning / dev / final_seen / holdout2 / synthetic_robust
python -m evaluation.compare --from-predictions evaluation/results/compare_predictions.json   # verify reproducibility
python -m evaluation.stability --version classify-v1   # live re-run vs recorded labels (needs Ollama)
```

classify-v2 is the default prompt for new analyses since 29 Oct 2026 (promotion record in DECISION_NOTE.md). The approved report and the evaluation of record are classify-v1 results; reproduce that run with `python -m app.cli analyse --provider replay --prompt-version classify-v1`.

## Example workflow (analyse → edit → submit → approve/reject → export)

bash (PowerShell users: run in Git Bash, or use the console at `/`):

```bash
A="Authorization: Bearer $(grep ^ANALYST_TOKEN .env | cut -d= -f2)"
R="Authorization: Bearer $(grep ^REVIEWER_TOKEN .env | cut -d= -f2)"
J="Content-Type: application/json"; H=http://localhost:8000

curl -s -X POST $H/datasets/pack -H "$A"                         # import + validate (re-run: all 'reused')
AID=$(curl -s -X POST $H/analyses -H "$A" -H "$J" -d '{"provider":"replay"}' | python -c "import sys,json;print(json.load(sys.stdin)['analysis_id'])")
curl -s $H/analyses/$AID -H "$A"                                 # status, counts, scorecard
RID=$(curl -s -X POST $H/reports -H "$A" -H "$J" -d "{\"analysis_id\":\"$AID\"}" | python -c "import sys,json;print(json.load(sys.stdin)['report_id'])")
curl -s -X PATCH $H/reports/$RID -H "$A" -H "$J" -d '{"base_version":1,"analyst_notes":"Checked D1-D3 quotes."}'
curl -s -X POST $H/reports/$RID/submit -H "$A" -H "$J" -d '{"version":1}'
SHA=$(curl -s $H/reports/$RID/versions/1 -H "$R" | python -c "import sys,json;print(json.load(sys.stdin)['content_sha256'])")

# wrong role -> 403
curl -s -X POST $H/reports/$RID/decision -H "$A" -H "$J" -d "{\"version\":1,\"decision\":\"approve\",\"comment\":\"self-approval\",\"content_sha256\":\"$SHA\"}"
# reviewer approves (or "reject" with a reason; a rejected version can never be exported)
curl -s -X POST $H/reports/$RID/decision -H "$R" -H "$J" -d "{\"version\":1,\"decision\":\"approve\",\"comment\":\"Evidence verified.\",\"content_sha256\":\"$SHA\"}"
curl -s $H/reports/$RID/export -H "$A"                           # 200: exactly approved v1

# edit after approval -> new draft v2; export of latest is refused until v2 is reviewed
curl -s -X PATCH $H/reports/$RID -H "$A" -H "$J" -d '{"base_version":1,"title":"Revised title"}'
curl -s $H/reports/$RID/export -H "$A"                           # 409 not_approved
curl -s "$H/reports/$RID/export?version=1" -H "$A"               # 200: old approved v1, marked superseded
```

## Model modes

| Mode | How | Use |
|---|---|---|
| `replay` (default) | `MODEL_PROVIDER=replay` or `{"provider":"replay"}` | Keyless; reproduces the recorded local-model run. A recording made for a different prompt or answer is refused (input SHA-256 check). |
| `local_model` | `{"provider":"ollama"}` or `python -m app.cli analyse --provider ollama --record` | Real model calls; `--record` refreshes replay files. |
| `stub` | `{"provider":"stub"}` | Deterministic baseline output for engineering tests. Not model quality. |

No hosted API is used or needed. No credentials beyond the two local tokens exist.

## Outputs

* `outputs/analysis_output.json`: per-response results, scores, coverage, diagnostics and remedies (`python -m app.cli write-output <analysis_id>`).
* `outputs/approved_report_export.json`: the exported, reviewer-approved report version.
* `evaluation/results/`: evaluation report and raw metrics.

## Layout

```
app/            FastAPI app: api/ routes, services/ (ingestion, analyzer, llm, scoring, reporting, review), db/ schema
prompts/        versioned model prompts (classify_v1.md production, classify_v2.md candidate)
replay/         recorded local-model outputs for keyless replay
evaluation/     labelled cases, builder, runner, results, FAILURES.md
tests/          pytest suite + synthetic fixture pack
claude-code/    implementation instructions, steps, decisions, handoff, quality gates
```

## Docker (public-safe demo image)

```bash
docker build -t answerscope-demo .
docker run -p 8000:8000 -e ANALYST_TOKEN=<random> -e REVIEWER_TOKEN=<random> answerscope-demo
```

The image contains code, prompts and the **synthetic** mini fixture pack only (stub provider). The supplied pack, replay recordings, outputs and evaluation data are excluded by `.dockerignore`, so the image is safe to run anywhere. On start it imports the fixture pack and runs a stub analysis, so the console has data; the full workflow (analyse → edit → submit → approve/reject → export) works on it.

**Hosted demo:** https://answerscope-demo.onrender.com (Render, free plan, built from this Dockerfile; created 29 Oct 2026). It runs the same public-safe image: synthetic mini pack, stub provider, no supplied data. Each start seeds an unsubmitted draft report (`python -m app.cli draft-report`), so a visitor can try the analyst edit, submit and reviewer decision steps; nothing is submitted or approved automatically. Tokens are Render environment variables, not stored in this repository; ask the repository owner for them. The database is in `/tmp`, so it resets when the free instance restarts or sleeps; the first request after a sleep can take about a minute.

**Privacy:** `assignment/` (supplied data) is git-ignored. `replay/`, `outputs/` and `evaluation/` contain excerpts of the supplied answers, so keep this repository private.
