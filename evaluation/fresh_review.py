"""Build fresh-v2 from frozen fresh-v1 plus the candidate's decisions on the AI audit.

  evaluation/cases/fresh_v1.jsonl            frozen 2026-10-29 (never modified)
  evaluation/cases/fresh_v1_ai_audit.md      AI second-pass audit (items for the candidate)
  evaluation/cases/fresh_review_log.jsonl    one record per candidate decision (last record per case wins)
  evaluation/cases/fresh_v2.jsonl            written here

  python -m evaluation.fresh_review

Supported changes: expected_set ({label: bool}) and evidence_replace ({label: [excerpts]}).
Excerpts are located in the answer and stored as exact raw spans; the expected score is
recomputed with vis-v1. Cases without a log record keep their fresh-v1 labels: the audit
proposed no change for them, and the candidate did not re-read them individually.
"""
from __future__ import annotations

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


def main() -> int:
    v1 = _jsonl(V1)
    decisions = {d["case_id"]: d for d in _jsonl(LOG)}
    unknown = set(decisions) - {c["case_id"] for c in v1}
    if unknown:
        print(f"BUILD FAILED: decisions for unknown cases {sorted(unknown)}")
        return 1
    bodies = {json.loads(l)["response_id"]: answer_body(json.loads(l)["answer_text"])
              for l in PACK.read_text(encoding="utf-8").splitlines()}
    out, errors = [], []
    for c in v1:
        new = copy.deepcopy(c)
        new["label_version"], new["labeller"] = "fresh-v2", LABELLER
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
    V2.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in out), encoding="utf-8")
    changed = [x["case_id"] for x in out if x["expected"] != next(c for c in v1 if c["case_id"] == x["case_id"])["expected"]]
    print(f"wrote {V2}: {len(out)} cases; labels changed: {changed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
