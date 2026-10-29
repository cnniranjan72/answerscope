"""Build labels-v3 from frozen labels-v2 plus the candidate's case-by-case review.

  evaluation/cases/labels_v2.jsonl              frozen 2026-10-28 (never modified)
  evaluation/cases/candidate_review_log.jsonl   one record per candidate decision (append-only;
                                                the last record for a case wins)
  evaluation/cases/labels_v3.jsonl              written here; default for run_eval

  python -m evaluation.candidate_review

Supported changes: ambiguous_add (label list) and evidence_replace ({label: [excerpts]}).
Every excerpt is located in the source answer and stored as an exact raw span; the
expected score is recomputed with vis-v1. Fails if any case lacks a candidate decision.
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
V2, LOG, V3 = CASES / "labels_v2.jsonl", CASES / "candidate_review_log.jsonl", CASES / "labels_v3.jsonl"
PACK = ROOT / "assignment" / "data" / "responses.jsonl"


def _jsonl(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def main() -> int:
    v2 = _jsonl(V2)
    decisions = {d["case_id"]: d for d in _jsonl(LOG)}  # last decision per case wins
    missing = [c["case_id"] for c in v2 if c["case_id"] not in decisions]
    if missing:
        print(f"cannot build labels-v3: no candidate decision for {missing}")
        return 1
    bodies = {json.loads(l)["response_id"]: answer_body(json.loads(l)["answer_text"])
              for l in PACK.read_text(encoding="utf-8").splitlines()}

    out, errors = [], []
    for c in v2:
        d = decisions[c["case_id"]]
        new = copy.deepcopy(c)
        new["label_version"] = "labels-v3"
        ch = d["changes"]
        new["ambiguous_labels"] = sorted(set(c["ambiguous_labels"]) | set(ch.get("ambiguous_add", [])))
        body = c["answer_text"] if c.get("synthetic") else bodies[c["response_id"]]
        for lab, excerpts in ch.get("evidence_replace", {}).items():
            new["evidence"][lab] = excerpts
            new["evidence_spans"][lab] = []
            for q in excerpts:
                loc = locate(q, body)
                if loc is None:
                    errors.append(f"{c['case_id']} {lab}: excerpt not found: {q!r}")
                    continue
                new["evidence_spans"][lab].append({"excerpt": q, "quote": body[loc[0]:loc[1]],
                                                   "start": loc[0], "end": loc[1]})
        score = scoring.score(scoring.components(new["expected"], {"first_party_cited": new["first_party_cited"]}))
        if score != new["expected_score"]:
            errors.append(f"{c['case_id']}: expected_score {new['expected_score']} != vis-v1 {score}")
        new["review"]["candidate_review"] = {"decision": d["decision"], "changes": ch, "reason": d["reason"],
                                             "recorded_at": d["recorded_at"]}
        new["review"]["labeller"] = (
            "drafted by AI coding assistant (Claude Code); every case reviewed and decided by the candidate on "
            "2026-10-29 (log: candidate_review_log.jsonl), using an AI-assisted second-opinion audit as input; "
            "single annotator, not independently double-annotated")
        new["review"]["frozen_at"] = "2026-10-29"
        out.append(new)

    if errors:
        print("BUILD FAILED:\n" + "\n".join(errors))
        return 1
    V3.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in out), encoding="utf-8")
    changed = [x["case_id"] for x in out if x["review"]["candidate_review"]["decision"] != "keep"]
    print(f"wrote {V3}: {len(out)} cases; changed by candidate: {changed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
