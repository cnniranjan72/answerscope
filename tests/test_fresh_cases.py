"""fresh-v1 integrity: frozen before classify-v2 was run on it, disjoint from labels-v3,
and split by prompt so holdout2 shares no prompt with dev or the earlier tuning cases."""
import hashlib
import json
from pathlib import Path

CASES = Path(__file__).resolve().parents[1] / "evaluation" / "cases"
FRESH_SHA256 = "c144389e444477892b0faf8fec14663301054e3173b8f047e1e3ebb38dd55200"  # frozen 2026-10-29, before any classify-v2 call on these answers
FRESH_V2_SHA256 = "e5efcf2ddc070908c276dcc8ac0110c0dc8b81cd6e6dbe1bf0798e52d447cf29"  # fresh-v1 + candidate decisions on the AI audit, 2026-10-29


def load(name):
    return [json.loads(l) for l in (CASES / name).read_text(encoding="utf-8").splitlines() if l.strip()]


def test_fresh_set_is_frozen():
    data = (CASES / "fresh_v1.jsonl").read_bytes().replace(b"\r\n", b"\n")
    assert hashlib.sha256(data).hexdigest() == FRESH_SHA256


def test_fresh_set_is_disjoint_and_split_by_prompt():
    fresh, v3 = load("fresh_v1.jsonl"), load("labels_v3.jsonl")
    assert len({c["case_id"] for c in fresh}) == len(fresh) == 36
    assert not {c["response_id"] for c in fresh} & {c["response_id"] for c in v3}
    dev = {c["prompt_id"] for c in fresh if c["split"] == "dev"}
    hold = {c["prompt_id"] for c in fresh if c["split"] == "holdout2"}
    assert dev and hold and not dev & hold
    assert not hold & {c["prompt_id"] for c in v3}


def test_fresh_v2_is_frozen_and_differs_from_v1_only_by_logged_decisions():
    data = (CASES / "fresh_v2.jsonl").read_bytes().replace(b"\r\n", b"\n")
    assert hashlib.sha256(data).hexdigest() == FRESH_V2_SHA256
    v1 = {c["case_id"]: c for c in load("fresh_v1.jsonl")}
    v2 = {c["case_id"]: c for c in load("fresh_v2.jsonl")}
    log = load("fresh_review_log.jsonl")
    assert v1.keys() == v2.keys() and all(v1[k]["split"] == v2[k]["split"] for k in v1)
    assert all(d["decided_by"] == "candidate" for d in log)
    changed = {k for k in v1 if v1[k]["expected"] != v2[k]["expected"]}
    assert changed == {d["case_id"] for d in log if d["decision"] == "change"} == {"D-017-aimode"}
