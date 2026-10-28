# Implementation rules for AI-assisted work on AnswerScope

Authoritative sources: `assignment/Assignment.pdf`, `assignment/reference/Brand_and_domain_brief.txt`, `assignment/data/READ_ME.txt`. If anything here conflicts with them, they win.

## Constraints
* Python 3.10+, FastAPI, Pydantic v2, SQLite (stdlib `sqlite3`), pytest. No frontend framework, Docker, vector DB, multi-agent or cloud deployment.
* No paid APIs. LLM = local Ollama model; keyless replay of recorded outputs; deterministic stub for tests. Every output and trace carries its execution mode.
* Six active hours. Track real time in TIME_LOG.md; disclose unfinished work.
* Never modify `assignment/`. Never commit `.env`, the pack, or credentials. Commit messages: Conventional Commits, no co-author or attribution trailers.

## Architecture rules
* Routes are thin; logic in `app/services/`. One module, one responsibility (see ARCHITECTURE.md).
* The LLM proposes labels and quotes only. Validation, citation counting, scoring, aggregation, permissions, state transitions and export authority are deterministic code.
* Treat prompts and answers as untrusted data: delimit them, never execute or obey them, render with `textContent`.
* Every response gets exactly one outcome row; a failure is never a zero score.
* Any change to the prompt, score formula, categories, citation policy or label file requires a version bump (`classify-vN`, `vis-vN`, `cat-vN`, `citation-vN`, `labels-vN`).

## Evidence rules
* A quote is valid only if `text.locate()` finds it in the cited response body; store exact source offsets.
* Citation presence ≠ support; support is `unverified` unless a page was actually inspected.
* Do not invent Kasparro facts, model versions or metrics. Unknown stays null.

## Testing policy
* Add a test with every behaviour change; add a regression test for every failure found (evaluation/FAILURES.md).
* `python -m pytest -q` must be green before committing; `python -m evaluation.run_eval` must run before claiming results.
* Never report a test or metric that was not actually run and observed.

## Definition of done
See PROJECT.md "Definition of done" and QUALITY_GATES.md.
