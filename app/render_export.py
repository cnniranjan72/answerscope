"""Render a verified, approved export as a readable Markdown report.

  python -m app.render_export outputs/approved_report_export.json --out report.md
  python -m app.render_export export.json --answers assignment/data/responses.jsonl --out report.md

The file is verified first (app.verify_export). If any check fails, nothing is rendered
and the exit code is 1: a tampered or unapproved file cannot become a readable report.
The rendering adds no claims; every sentence comes from the approved content, and the
header states the content hash and the approval it carries.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from app.verify_export import load_answers, verify


def _plain(quote: str) -> str:
    """Display form of a quote: citation markers, link targets and bold markers removed."""
    q = re.sub(r"\[(?:\[\d+\])?\]\([^)\s]*\)", "", quote)
    q = re.sub(r"\[([^\]]*)\]\([^)\s]*\)", r"\1", q)
    return " ".join(q.replace("**", "").replace("__", "").split())


def _rate(cell: dict | None) -> str:
    if not cell or cell.get("rate") is None:
        return "–"
    lo, hi = cell["ci95"]
    return f"{cell['count']}/{cell['denominator']} ({100 * cell['rate']:.0f}%, 95% CI {100 * lo:.0f}–{100 * hi:.0f}%)"


def render(doc: dict) -> str:
    c, a, p = doc["content"], doc["approval"], doc["content"].get("provenance", {})
    L = [f"# {c['title']}", "",
         f"> Approved report `{doc['report_id']}` version {doc['version']}. Approved by {a['reviewer']} on {a['decided_at']}. "
         f"Content SHA-256 `{doc['content_sha256']}`; verify with `python -m app.verify_export`."
         + ("" if doc.get("is_latest_version", True) else f" **Superseded by version {doc.get('superseded_by_version')}.**"), "",
         "## Summary", "", c.get("executive_summary", ""), ""]
    if c.get("analyst_notes"):
        L += ["**Analyst notes.** " + c["analyst_notes"], ""]
    L += [f"**Reviewer's comment.** {a.get('comment', '')}", "", "## Scorecard", "",
          "| Segment | Mentioned | Recommended | Negative | Entity confusion | Mean score | Succeeded |", "|---|---|---|---|---|---|---|"]
    sc = c.get("scorecard", {})
    for name, cell in [("All answers", sc.get("overall"))] + list((sc.get("by_segment") or {}).items()):
        if cell:
            L.append(f"| {name} | {_rate(cell.get('mentioned'))} | {_rate(cell.get('recommended'))} | {_rate(cell.get('negative'))} | "
                     f"{_rate(cell.get('entity_confusion'))} | {cell.get('mean_score', '–')} | {cell.get('succeeded')}/{cell.get('eligible')} |")
    L += ["", "## Diagnostics", ""]
    for d in sorted(c.get("diagnostics", []), key=lambda x: x.get("priority", 0)):
        L += [f"### {d['id']}. {d['title']} ({d.get('kind', '')})", "", d.get("observation", ""), "",
              f"**Hypothesis.** {d.get('hypothesis', '')}", "", f"**How to test.** {d.get('how_to_test', '')}", "", "**Evidence**", ""]
        L += [f"- “{_plain(e['quote'])}” ({e.get('engine', '?')}; question: “{e.get('question', '?')}”)" for e in d.get("evidence", [])]
        L.append("")
    L += ["## Remedies", ""]
    for r in sorted(c.get("remedies", []), key=lambda x: x.get("priority", 0)):
        L += [f"### {r['id']}. Priority {r.get('priority')} (addresses {r.get('diagnostic_id')}; effort {r.get('effort')})", "",
              r.get("action", ""), "", f"- **Problem:** {r.get('problem', '')}", f"- **Expected benefit:** {r.get('expected_benefit', '')}",
              f"- **Effort:** {r.get('effort_detail', '')}", f"- **Uncertainty:** {r.get('uncertainty', '')}",
              f"- **Validation:** {r.get('validation', '')}", ""]
    L += ["## Limitations", ""] + [f"- {x}" for x in c.get("limitations", [])] + [
        "", "## Method", "",
        "| Item | Value |", "|---|---|"] + [f"| {k} | {p[k]} |" for k in (
            "prompt_version", "model", "execution_mode", "score_version", "category_version", "citation_policy",
            "report_generator", "historical_capture_date", "analysis_id") if p.get(k)] + [""]
    return "\n".join(L)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m app.render_export", description=__doc__.split("\n")[0])
    ap.add_argument("export_file", type=Path)
    ap.add_argument("--answers", type=Path, help="responses.jsonl: also verify every quote location before rendering")
    ap.add_argument("--out", type=Path, help="write the Markdown here (default: stdout)")
    args = ap.parse_args(argv)
    doc = json.loads(args.export_file.read_text(encoding="utf-8"))
    failed = [f"{n}: {d}" for n, ok, d in verify(doc, load_answers(args.answers) if args.answers else None) if not ok]
    if failed:
        print("REFUSED: the export did not verify; nothing rendered.\n" + "\n".join(failed), file=sys.stderr)
        return 1
    md = render(doc)
    if args.out:
        args.out.write_text(md, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        sys.stdout.write(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
