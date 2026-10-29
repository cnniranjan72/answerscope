"""Build fresh-v2 from frozen fresh-v1 plus the candidate's decisions on the AI audit.

  evaluation/cases/fresh_v1.jsonl            frozen 2026-10-29 (never modified)
  evaluation/cases/fresh_v1_ai_audit.md      AI second-pass audit (items for the candidate)
  evaluation/cases/fresh_review_log.jsonl    one record per candidate decision (last record per case wins)
  evaluation/cases/fresh_v2.jsonl            written here

  python -m evaluation.fresh_review     rebuild fresh-v2; refuses to overwrite it if the result differs

A written label set is frozen. Later decisions go to a new log and a new label version:

  python -m evaluation.fresh_review --log evaluation/cases/fresh_review_log.jsonl \
      --log evaluation/cases/fresh_review_log_v3.jsonl --out evaluation/cases/fresh_v3.jsonl --label-version fresh-v3

Supported changes: expected_set ({label: bool}) and evidence_replace ({label: [excerpts]}).
Excerpts are located in the answer and stored as exact raw spans; the expected score is
recomputed with vis-v1. Cases without a log record keep their fresh-v1 labels: the audit
proposed no change for them, and the candidate did not re-read them individually.
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

from app.services import scoring
from app.services.text import answer_body, locate

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "evaluation" / "cases"
V1, LOG, V2 = CASES / "fresh_v1.jsonl", CASES / "fresh_review_log.jsonl", CASES / "fresh_v2.jsonl"
PACK = ROOT / "assignment" / "data" / "responses.jsonl"
LABELLER = ("drafted by AI coding assistant (Claude Code) blind to model predictions; AI second-pass audit "
            "(fresh_v1_ai_audit.md); the candidate decided the 4 audit items by accepting the AI suggestions "
            "(fresh_review_log.jsonl); other cases not individually re-read by the candidate")


def _jsonl(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def _labeller(version: str, decided: int) -> str:
    if version == "fresh-v2":
        return LABELLER  # wording of the frozen fresh-v2 set
    return ("drafted by AI coding assistant (Claude Code) blind to model predictions; AI second-pass audit "
            f"(fresh_v1_ai_audit.md); the candidate decided {decided} cases (decision logs); "
            "other cases keep the AI-drafted fresh-v1 labels")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m evaluation.fresh_review")
    ap.add_argument("--log", action="append", type=Path,
                    help="decision log; repeatable, later records win (default: the fresh-v2 log)")
    ap.add_argument("--out", type=Path, default=V2)
    ap.add_argument("--label-version", default="fresh-v2")
    args = ap.parse_args(argv)
    v1 = _jsonl(V1)
    decisions = {d["case_id"]: d for log in (args.log or [LOG]) for d in _jsonl(log)}
    unknown = set(decisions) - {c["case_id"] for c in v1}
    if unknown:
        print(f"BUILD FAILED: decisions for unknown cases {sorted(unknown)}")
        return 1
    bodies = {json.loads(l)["response_id"]: answer_body(json.loads(l)["answer_text"])
              for l in PACK.read_text(encoding="utf-8").splitlines()}
    out, errors = [], []
    for c in v1:
        new = copy.deepcopy(c)
        new["label_version"], new["labeller"] = args.label_version, _labeller(args.label_version, len(decisions))
        d = decisions.get(c["case_id"])
        if d:
            ch = d["changes"]
            new["expected"].update(ch.get("expected_set", {}))
            for lab, excerpts in ch.get("evidence_replace", {}).items():
                new["evidence"][lab], new["evidence_spans"][lab] = excerpts, []
                for q in excerpts:
                    loc = locate(q, bodies[c["response_id"]])
                    if loc is None:
                        errors.append(f"{c['case_id']} {lab}: excerpt not found: {q!r}")
                        continue
                    new["evidence_spans"][lab].append({"excerpt": q, "quote": bodies[c["response_id"]][loc[0]:loc[1]],
                                                       "start": loc[0], "end": loc[1]})
            new["candidate_decision"] = {k: d[k] for k in ("audit_item", "decision", "reason", "basis", "recorded_at")}
        for lab in ("recommended", "negative", "entity_confusion"):
            if new["expected"][lab] and not new["evidence"].get(lab):
                errors.append(f"{c['case_id']}: true label {lab} has no evidence")
        new["expected_score"] = scoring.score(scoring.components(new["expected"],
                                                                 {"first_party_cited": new["first_party_cited"]}))
        out.append(new)
    if errors:
        print("BUILD FAILED:\n" + "\n".join(errors))
        return 1
    text = "".join(json.dumps(x, ensure_ascii=False) + "\n" for x in out)
    changed = [x["case_id"] for x in out if x["expected"] != next(c for c in v1 if c["case_id"] == x["case_id"])["expected"]]
    if args.out.exists():  # a written label set is frozen (CLAUDE.md: label changes get a new version)
        if args.out.read_text(encoding="utf-8").replace("\r\n", "\n") == text:
            print(f"unchanged: {args.out} reproduces from its decision logs ({len(out)} cases)")
            return 0
        print(f"REFUSED: {args.out} exists and the rebuild differs; label sets are frozen. Put new decisions in "
              "a new log and build a new version (--out evaluation/cases/fresh_v3.jsonl --label-version fresh-v3).")
        return 1
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {args.out}: {len(out)} cases; labels changed vs fresh-v1: {changed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
