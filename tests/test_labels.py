"""Label-file integrity (regressions from the rubric-v2 audit): splits stay separate,
expected scores follow vis-v1, and every evidence span is an exact raw span of the source."""
import json
from pathlib import Path

import pytest

from app.services import scoring
from app.services.text import answer_body, locate

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "evaluation" / "cases"
FILES = sorted(CASES.glob("labels_*.jsonl"))
PACK = ROOT / "assignment" / "data" / "responses.jsonl"
LABELS = ["mentioned", "recommended", "negative", "entity_confusion"]


def load(path):
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def bodies():
    if not PACK.exists():
        return None
    return {json.loads(l)["response_id"]: answer_body(json.loads(l)["answer_text"])
            for l in PACK.read_text(encoding="utf-8").splitlines()}


@pytest.mark.parametrize("path", FILES, ids=lambda p: p.name)
def test_splits_and_synthetic_marking(path):
    cases = load(path)
    ids = [c["case_id"] for c in cases]
    assert len(ids) == len(set(ids))
    assert {c["split"] for c in cases} <= {"tuning", "holdout", "synthetic"}
    for c in cases:
        assert (c["split"] == "synthetic") == bool(c.get("synthetic")) == (c["response_id"] is None)
    real = [c for c in cases if c["split"] != "synthetic"]
    assert len({c["engine"] for c in real}) == 3 and len(real) >= 8
    assert len([c for c in cases if c["split"] == "synthetic"]) >= 2
    tuning = {c["response_id"] for c in cases if c["split"] == "tuning"}
    holdout = {c["response_id"] for c in cases if c["split"] == "holdout"}
    assert not tuning & holdout


@pytest.mark.parametrize("path", FILES, ids=lambda p: p.name)
def test_expected_scores_follow_vis_v1(path):
    for c in load(path):
        exp = scoring.score(scoring.components(c["expected"], {"first_party_cited": c["first_party_cited"]}))
        assert exp == c["expected_score"], c["case_id"]
        assert not (c["expected"]["recommended"] and not c["expected"]["mentioned"]), c["case_id"]


@pytest.mark.parametrize("path", FILES, ids=lambda p: p.name)
def test_every_excerpt_maps_to_source(path):
    texts = bodies()
    for c in load(path):
        body = c["answer_text"] if c.get("synthetic") else (texts or {}).get(c["response_id"])
        if body is None:
            continue  # private pack not present: real-case checks skipped
        for lab, quotes in c["evidence"].items():
            assert c["expected"][lab], f"{c['case_id']}: evidence for false label {lab}"
            for q in quotes:
                assert locate(q, body) is not None, (c["case_id"], q)


def test_v2_spans_are_exact_raw_offsets():
    """Audit finding: v1 stored normalised excerpts (e.g. T05 without '**'); v2 stores the
    exact raw span with offsets so evidence resolves to the original answer."""
    path = CASES / "labels_v2_proposed.jsonl"
    if not path.exists():
        pytest.skip("no proposed revision")
    texts = bodies()
    for c in load(path):
        for lab in LABELS:
            if c["expected"][lab] and lab in c["evidence"]:
                assert c["evidence_spans"].get(lab), (c["case_id"], lab)
        body = c["answer_text"] if c.get("synthetic") else (texts or {}).get(c["response_id"])
        if body is None:
            continue
        for spans in c["evidence_spans"].values():
            for s in spans:
                assert body[s["start"]:s["end"]] == s["quote"], c["case_id"]
        assert c["review"]["labeller"].startswith("AI coding assistant")  # never presented as human-verified
