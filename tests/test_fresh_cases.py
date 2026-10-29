"""fresh-v1 integrity: frozen before classify-v2 was run on it, disjoint from labels-v3,
and split by prompt so holdout2 shares no prompt with dev or the earlier tuning cases."""
import hashlib
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "evaluation" / "cases"
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


@pytest.mark.skipif(not (ROOT / "assignment" / "data" / "responses.jsonl").exists(),
                    reason="needs the supplied pack (not in CI)")
def test_fresh_review_reproduces_v2_and_refuses_to_overwrite_a_frozen_set(tmp_path, capsys):
    from evaluation import fresh_review
    before = (CASES / "fresh_v2.jsonl").read_bytes()
    assert fresh_review.main([]) == 0 and "unchanged" in capsys.readouterr().out
    extra = tmp_path / "log_v3.jsonl"
    extra.write_text(json.dumps({"case_id": "D-004-aimode", "audit_item": None, "decision": "change",
                                 "changes": {"expected_set": {"mentioned": True}}, "reason": "test", "decided_by": "test",
                                 "basis": "test", "recorded_at": "2026-10-29T00:00"}) + "\n", encoding="utf-8")
    log = CASES / "fresh_review_log.jsonl"
    frozen = tmp_path / "frozen.jsonl"
    frozen.write_text("not the rebuild\n", encoding="utf-8")
    assert fresh_review.main(["--log", str(log), "--log", str(extra), "--out", str(frozen)]) == 1
    assert frozen.read_text(encoding="utf-8") == "not the rebuild\n" and "REFUSED" in capsys.readouterr().out
    out = tmp_path / "fresh_v3.jsonl"
    assert fresh_review.main(["--log", str(log), "--log", str(extra), "--out", str(out),
                              "--label-version", "fresh-v3"]) == 0
    v3 = [json.loads(l) for l in out.read_text(encoding="utf-8").splitlines()]
    assert {c["label_version"] for c in v3} == {"fresh-v3"} and "decided 6 cases" in v3[0]["labeller"]
    assert (CASES / "fresh_v2.jsonl").read_bytes() == before
