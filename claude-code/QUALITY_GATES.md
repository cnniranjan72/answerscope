# Quality gates

Each gate must be observed (command run, output seen) before moving on.

| Gate | Check | Command / evidence |
|---|---|---|
| G1 Inputs intact | Pack checker passes on untouched `assignment/` | `py -3 assignment/tools/check_pack.py` |
| G2 Ingestion | 50/150/2,439 inserted; second import all reused; 0 rejected | `POST /datasets/pack` twice |
| G3 Outcomes | Every response in the submitted analysis has exactly one outcome; failures have reasons and null scores | `GET /analyses/{id}` counts sum to 150 |
| G4 Tests | `pytest` green, no skips hiding required checks | `python -m pytest -q` |
| G5 Review control | Wrong role 403; rejected not exportable; edit-after-approval → new draft; stale export refused | tests + README curl sequence |
| G6 Evaluation | Report written; final split separate from tuning; baseline and model on same cases; arithmetic 0 mismatches; negative evidence case all detected | `python -m evaluation.run_eval` |
| G7 Evidence | Generated report has 0 evidence problems; every diagnostic cites response IDs + verbatim quotes | eval diagnostics check, submit succeeds |
| G8 Honesty | Execution mode shown on outputs; replay/stub not presented as model quality; unknowns null | read outputs/ and EVALUATION.md |
| G9 Secrets | No tokens, `.env` or pack in git | `git ls-files`, grep for token values |
| G10 Reproducibility | README steps work from a fresh clone + venv | clean-clone run recorded in HANDOFF.md |
