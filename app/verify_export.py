"""Verify an exported report file offline: no database, server or tokens needed.

  python -m app.verify_export outputs/approved_report_export.json
  python -m app.verify_export export.json --answers assignment/data/responses.jsonl

Checks:
  * the format is a known export format;
  * content_sha256 matches the content, recomputed as the export states (canonical JSON
    after removing the export-only evidence fields), so any edit after approval is detected;
  * the export records an approval;
  * structure: 3 diagnostics and 3 remedies, and every remedy quote is drawn from its diagnostic;
  * with --answers (the supplied responses.jsonl): every quote is found in the cited answer at
    the stated location.
Exit code 0 when every check passes, 1 otherwise. Checks prove integrity and provenance of
the file; they do not prove that the cited sources support the claims.
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

from app.services.reporting import canonical, sha256
from app.services.review import EXPORT_EVIDENCE_FIELDS
from app.services.text import answer_body, locate

FORMATS = {"answerscope-report-export-v1"}


def verify(doc: dict, answers: dict[str, str] | None = None) -> list[tuple[str, bool, str]]:
    checks: list[tuple[str, bool, str]] = []
    checks.append(("format", doc.get("export_format") in FORMATS, str(doc.get("export_format"))))
    content = copy.deepcopy(doc.get("content") or {})
    for section in ("diagnostics", "remedies"):
        for item in content.get(section, []):
            for e in item.get("evidence", []):
                for k in EXPORT_EVIDENCE_FIELDS:
                    e.pop(k, None)
    actual = sha256(canonical(content))
    checks.append(("content hash", actual == doc.get("content_sha256"),
                   f"recomputed {actual[:16]}…, stated {str(doc.get('content_sha256'))[:16]}…"))
    appr = doc.get("approval") or {}
    checks.append(("approval", appr.get("decision") == "approved" and bool(appr.get("reviewer")),
                   f"{appr.get('decision')} by {appr.get('reviewer')} at {appr.get('decided_at')}"))
    diags, rems = doc["content"].get("diagnostics", []), doc["content"].get("remedies", [])
    checks.append(("three diagnostics and three remedies", len(diags) == 3 and len(rems) == 3,
                   f"{len(diags)} diagnostics, {len(rems)} remedies"))
    by_id = {d["id"]: {(e["response_id"], e["quote"]) for e in d.get("evidence", [])} for d in diags}
    stray = [f"{r['id']}" for r in rems
             if not {(e["response_id"], e["quote"]) for e in r.get("evidence", [])} <= by_id.get(r.get("diagnostic_id"), set())]
    checks.append(("remedy evidence comes from its diagnostic", not stray, ", ".join(stray) or "all remedies"))
    if answers is not None:
        bad, n = [], 0
        for section in ("diagnostics", "remedies"):
            for item in doc["content"].get(section, []):
                for i, e in enumerate(item.get("evidence", []), start=1):
                    n += 1
                    body = answers.get(e["response_id"])
                    loc = e.get("location") or {}
                    found = locate(e["quote"], answer_body(body)) if body is not None else None
                    if found is None or (loc and (loc.get("start"), loc.get("end")) != found):
                        bad.append(f"{item['id']}#{i}")
        checks.append(("quotes found in the cited answers at the stated location", not bad,
                       f"{n - len(bad)}/{n} verified" + (f"; failed: {', '.join(bad)}" if bad else "")))
    return checks


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m app.verify_export", description=__doc__.split("\n")[0])
    ap.add_argument("export_file", type=Path)
    ap.add_argument("--answers", type=Path, help="responses.jsonl of the analysed dataset (verifies every quote)")
    args = ap.parse_args(argv)
    doc = json.loads(args.export_file.read_text(encoding="utf-8"))
    answers = None
    if args.answers:
        answers = {}
        for line in args.answers.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                answers[r["response_id"]] = r["answer_text"]
    checks = verify(doc, answers)
    for name, ok, detail in checks:
        print(f"{'PASS' if ok else 'FAIL'}  {name}: {detail}")
    ok = all(c[1] for c in checks)
    print(f"report {doc.get('report_id')} v{doc.get('version')}: " + ("verified" if ok else "NOT verified"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
