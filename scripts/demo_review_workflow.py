"""Demonstrates the review controls end to end against a throwaway database and writes a
transcript to outputs/review_workflow_demo.md:

  import -> analyse -> edit -> submit -> wrong-role denial -> reject -> export denied
  -> edit (new draft) -> submit -> approve -> export -> edit after approval -> export denied
  -> explicit export of the old approved version (marked superseded)

  python scripts/demo_review_workflow.py [--provider replay|stub]

The real report for submission is reviewed by a human in the console; this script only
proves the mechanics.
"""
from __future__ import annotations

import argparse
import sys
import tempfile
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient  # noqa: E402

from app.config import load_settings  # noqa: E402
from app.main import create_app  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", default="replay", choices=["replay", "stub"])
    args = ap.parse_args()
    base = load_settings()
    analyst = next(t for t, i in base.tokens.items() if i.role == "analyst")
    reviewer = next(t for t, i in base.tokens.items() if i.role == "reviewer")
    A, R = {"Authorization": f"Bearer {analyst}"}, {"Authorization": f"Bearer {reviewer}"}
    log: list[str] = []

    with tempfile.TemporaryDirectory() as tmp:
        c = TestClient(create_app(replace(base, db_path=Path(tmp) / "demo.db")))

        def step(label, method, url, headers, body=None, expect=None):
            r = c.request(method, url, headers=headers, json=body)
            data = r.json()
            who = "analyst" if headers is A else "reviewer"
            note = data.get("error", {}).get("code", "") if r.status_code >= 400 else ""
            ok = "" if expect is None else (" ✔" if r.status_code == expect else f" ✘ expected {expect}")
            log.append(f"| {label} | {who} | `{method} {url.replace(rid, '{id}') if rid else url}` "
                       f"| {r.status_code}{ok} | {note} |")
            if expect is not None and r.status_code != expect:
                raise SystemExit(f"unexpected status for {label}: {r.status_code} {data}")
            return data

        rid = None
        step("import pack", "POST", "/datasets/pack", A, expect=201)
        step("re-import (idempotent)", "POST", "/datasets/pack", A, expect=201)
        run = step(f"analyse ({args.provider})", "POST", "/analyses", A, {"provider": args.provider}, expect=201)
        rep = step("create draft report", "POST", "/reports", A, {"analysis_id": run["analysis_id"]}, expect=201)
        rid = rep["report_id"]
        step("edit draft v1", "PATCH", f"/reports/{rid}", A, {"base_version": 1, "analyst_notes": "Demo edit."}, expect=200)
        step("submit v1", "POST", f"/reports/{rid}/submit", A, {"version": 1}, expect=200)
        sha1 = step("read v1", "GET", f"/reports/{rid}/versions/1", R, expect=200)["content_sha256"]
        step("analyst tries to approve", "POST", f"/reports/{rid}/decision", A,
             {"version": 1, "decision": "approve", "comment": "self-approve", "content_sha256": sha1}, expect=403)
        step("reviewer rejects v1", "POST", f"/reports/{rid}/decision", R,
             {"version": 1, "decision": "reject", "comment": "Tighten D1 wording.", "content_sha256": sha1}, expect=200)
        step("export rejected v1", "GET", f"/reports/{rid}/export?version=1", A, expect=409)
        step("edit -> new draft v2", "PATCH", f"/reports/{rid}", A, {"base_version": 1, "analyst_notes": "Addressed review."}, expect=200)
        step("export unreviewed v2", "GET", f"/reports/{rid}/export", A, expect=409)
        step("submit v2", "POST", f"/reports/{rid}/submit", A, {"version": 2}, expect=200)
        sha2 = step("read v2", "GET", f"/reports/{rid}/versions/2", R, expect=200)["content_sha256"]
        step("approve with wrong hash", "POST", f"/reports/{rid}/decision", R,
             {"version": 2, "decision": "approve", "comment": "Approving with a stale hash.", "content_sha256": sha1}, expect=409)
        step("reviewer approves v2", "POST", f"/reports/{rid}/decision", R,
             {"version": 2, "decision": "approve", "comment": "Evidence checked.", "content_sha256": sha2}, expect=200)
        step("export approved v2", "GET", f"/reports/{rid}/export", A, expect=200)
        step("edit after approval -> v3", "PATCH", f"/reports/{rid}", A, {"base_version": 2, "title": "Changed after approval"}, expect=200)
        step("export latest (v3 draft)", "GET", f"/reports/{rid}/export", A, expect=409)
        old = step("export old approved v2 explicitly", "GET", f"/reports/{rid}/export?version=2", A, expect=200)
        step("approve draft v3 without submit", "POST", f"/reports/{rid}/decision", R,
             {"version": 3, "decision": "approve", "comment": "Approve unsubmitted draft.", "content_sha256": sha2}, expect=409)

    out = ROOT / "outputs" / "review_workflow_demo.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text(
        f"# Review workflow demonstration\n\nThrowaway database; analysis provider `{args.provider}` "
        f"(execution mode `{run['execution_mode']}`, counts {run['counts']}). Generated by "
        f"`python scripts/demo_review_workflow.py`. Every status matched its expectation (✔).\n\n"
        "| Step | Identity | Request | Status | Error code |\n|---|---|---|---|---|\n" + "\n".join(log)
        + f"\n\nOld approval export: version {old['version']}, superseded_by_version {old['superseded_by_version']}, "
        f"approved by {old['approval']['reviewer']}.\n", encoding="utf-8")
    print(f"all {len(log)} steps matched expectations; wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
