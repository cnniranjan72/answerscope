"""fresh-v1 integrity: frozen before classify-v2 was run on it, disjoint from labels-v3,
and split by prompt so holdout2 shares no prompt with dev or the earlier tuning cases."""
import hashlib
import json
from pathlib import Path

CASES = Path(__file__).resolve().parents[1] / "evaluation" / "cases"
FRESH_SHA256 = "c144389e444477892b0faf8fec14663301054e3173b8f047e1e3ebb38dd55200"  # frozen 2026-10-29, before any classify-v2 call on these answers


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
