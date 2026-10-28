# Prototype surface

The deliverable is the API; the console at `/` is a thin client over it (no extra authority).

## Analyst flow
1. Sign in with the analyst token. The server reports `name · analyst`.
2. **Import assignment pack** → counts of inserted / reused / rejected.
3. **Run** analysis (replay by default) → appears under Analyses with execution mode and eligible/ok/failed/skipped.
4. **Create report** → draft v1 with provenance, scorecard (engine × branded/unbranded with k/n), D1–D3, R1–R3, limitations.
5. **Edit draft** → PATCH with `base_version`. Editing a frozen version creates the next draft.
6. **Submit** → refused with the list of problems if any quote is not verbatim, or if a remedy does not follow from its diagnostic.

## Reviewer flow
1. Sign in with the reviewer token; import/edit controls are hidden, and the server would refuse them anyway (403).
2. Open the submitted version, read findings and quotes, enter a comment, then **Approve** or **Reject**. The console sends the version's content SHA-256.
3. Review history shows actor, decision, version, comment and time.

## Export
**Export vN** downloads JSON only if vN is approved. Otherwise the refusal (409) is shown with the latest approved version, if any. An older approved version is labelled superseded.

## Not built
Charts, search/filtering of per-response results in the UI (available via `GET /analyses/{id}/results`), user management, and notifications.
