"""Build the candidate's review sheet for the fresh-v2 labels not yet decided by the candidate.

  python -m evaluation.fresh_review_sheet            regenerate claude-code/FRESH_V2_REVIEW_SHEET.md
  python -m evaluation.fresh_review_sheet --check    exit 1 if the committed sheet is out of date

For each undecided case: the question, the AI-drafted labels, and the sentences that name
Kasparro or Kaspr. Model disagreement is in an appendix, to be read after deciding, so the
predictions do not anchor the decision. The sheet decides nothing.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from app.services.analyzer import sentence_bounds
from app.services.text import answer_body

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "evaluation" / "cases"
PACK = ROOT / "assignment" / "data" / "responses.jsonl"
PREDICTIONS = ROOT / "evaluation" / "results" / "compare_fresh_v2_predictions.json"
SHEET = ROOT / "claude-code" / "FRESH_V2_REVIEW_SHEET.md"
LABELS = ("mentioned", "recommended", "negative", "entity_confusion")
SHORT = {"mentioned": "M", "recommended": "R", "negative": "N", "entity_confusion": "C"}
_LINK = re.compile(r"\[\[?[^\]]*\]?\]\(https?://[^)]*\)")


def _jsonl(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def kasparro_sentences(body: str, limit_chars: int = 280) -> list[str]:
    """Distinct sentences naming Kasparro or Kaspr, link markup removed, in answer order."""
    seen, out = set(), []
    for m in re.finditer(r"\bkaspa?r", body, re.I):
        s, e = sentence_bounds(body, m.start(), m.end())
        if (s, e) in seen:
            continue
        seen.add((s, e))
        txt = " ".join(_LINK.sub("", body[s:e]).split())
        out.append(txt if len(txt) <= limit_chars else txt[:limit_chars - 3] + "...")
    return out


def build_sheet() -> str:
    cases = _jsonl(CASES / "fresh_v2.jsonl")
    decided = {d["case_id"] for d in _jsonl(CASES / "fresh_review_log.jsonl")}
    bodies = {d["response_id"]: answer_body(d["answer_text"]) for d in _jsonl(PACK)}
    preds = json.loads(PREDICTIONS.read_text(encoding="utf-8"))["predictions"]
    yn = lambda e: " ".join(f"{SHORT[k]}={'Y' if e[k] else 'n'}" for k in LABELS)
    todo = [c for c in cases if c["case_id"] not in decided]
    L = [f"# fresh-v2 label review sheet ({len(todo)} cases not yet read by the candidate)", "",
         "Prepared by the AI assistant from `evaluation/cases/fresh_v2.jsonl` and the supplied answers. **No label here has been decided by the candidate.** "
         "The labels were drafted by the AI blind to model predictions; this sheet lets the candidate confirm or change them.", "",
         "**How to use.** For each case, read the question, the Kasparro sentences and (if needed) the full answer, then mark ✅ keep or ✏️ change. "
         "The model-disagreement list is in the appendix: read it only after deciding, so the predictions do not anchor the decision.", "",
         "**Recording decisions.** Do not edit `fresh_v2.jsonl` (frozen). Add one JSON line per decided case to a new file "
         "`evaluation/cases/fresh_review_log_v3.jsonl` (template at the end), then build fresh-v3:", "",
         "```", "python -m evaluation.fresh_review --log evaluation/cases/fresh_review_log.jsonl --log evaluation/cases/fresh_review_log_v3.jsonl --out evaluation/cases/fresh_v3.jsonl --label-version fresh-v3", "```", "",
         "Rubric reminder (rubric-v2): R = the answer recommends Kasparro or states it suits the asker's need; N = unfavourable framing of Kasparro (doubt, weak track record, steer away), not a neutral description; "
         "C = the answer describes another entity as Kasparro (e.g. Kaspr) or misidentifies it; M = Kasparro is named.", ""]
    for i, c in enumerate(todo, 1):
        e, amb = c["expected"], c.get("ambiguous_labels") or []
        L += [f"## {i}. {c['case_id']} ({c['split']}, {c['engine']})", "", f"**Q:** {c['question']}", "",
              f"**AI-drafted labels:** {yn(e)}" + (f" · ambiguous: {', '.join(amb)}" if amb else "") + f" · expected score {c['expected_score']}", "",
              f"**AI note:** {c.get('note') or '—'}", ""]
        L += [f"- evidence for {lab}: \"{q}\"" for lab, qs in (c.get("evidence") or {}).items() for q in qs]
        ss = kasparro_sentences(bodies[c["response_id"]])
        L += ["", "**Sentences naming Kasparro/Kaspr:**" if ss else "**No sentence names Kasparro/Kaspr.**"]
        L += [f"> {s}" for s in ss[:5]] + ([f"> … {len(ss) - 5} more in the full answer"] if len(ss) > 5 else [])
        L += ["", f"Full answer: response_id `{c['response_id']}` in the console or the pack.", "", "Decision: ☐ keep ☐ change → ________", ""]
    L += ["## Appendix: model disagreement (read after deciding)", "",
          "Cases where classify-v1 or classify-v2 disagreed with the AI-drafted label in the fresh-v2 comparison. Disagreement does not mean the label is wrong.", "",
          "| Case | Label | AI-drafted | classify-v1 | classify-v2 |", "|---|---|---|---|---|"]
    fmt = lambda v: "failed" if v is None else ("Y" if v else "n")
    both = set()
    for c in todo:
        for lab in LABELS:
            v1, v2 = (None if not (p := preds[v].get(c["case_id"])) or p["status"] != "succeeded" else p["pred"]["labels"][lab]
                      for v in ("classify-v1", "classify-v2"))
            label = c["expected"][lab]
            if any(v is not None and v != label for v in (v1, v2)):
                L.append(f"| {c['case_id']} | {lab} | {fmt(label)} | {fmt(v1)} | {fmt(v2)} |")
                if fmt(v1) == fmt(v2) != fmt(label):
                    both.add(f"{c['case_id']} ({lab})")
    L += ["", f"Both prompts disagree with the AI-drafted label in {len(both)} places; if time is short, these are the cases worth re-reading first: "
          + ", ".join(sorted(both)) + "."]
    basis = "candidate read the answer (FRESH_V2_REVIEW_SHEET.md)"
    L += ["", "## Decision log template (one line per decided case)", "", "```json",
          json.dumps({"case_id": "D-004-aimode", "audit_item": None, "decision": "keep", "changes": {}, "reason": "<why>",
                      "decided_by": "candidate", "basis": basis, "recorded_at": "<YYYY-MM-DDTHH:MM>"}),
          json.dumps({"case_id": "<id>", "audit_item": None, "decision": "change",
                      "changes": {"expected_set": {"negative": True}, "evidence_replace": {"negative": ["<verbatim excerpt from the answer>"]}},
                      "reason": "<why>", "decided_by": "candidate", "basis": basis, "recorded_at": "<YYYY-MM-DDTHH:MM>"}),
          "```", "", "A label set to true needs at least one verbatim evidence excerpt, or the build fails. After building fresh-v3, add its hash pin and a `fresh-v3` entry in `evaluation/compare.py` before comparing."]
    return "\n".join(L) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m evaluation.fresh_review_sheet")
    ap.add_argument("--check", action="store_true", help="only report whether the committed sheet is current")
    args = ap.parse_args(argv)
    text = build_sheet()
    current = SHEET.read_text(encoding="utf-8").replace("\r\n", "\n") if SHEET.exists() else None
    if args.check:
        print("sheet is current" if current == text else "sheet is OUT OF DATE")
        return 0 if current == text else 1
    SHEET.write_text(text, encoding="utf-8")
    print(f"wrote {SHEET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
