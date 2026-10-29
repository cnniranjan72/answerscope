"""evaluation/compare.py must fail loudly instead of reporting numbers from bad inputs."""
import json
import shutil
from pathlib import Path

import pytest

from evaluation import compare

REAL = Path(compare.CASES)


@pytest.fixture
def cases_dir(tmp_path, monkeypatch):
    d = tmp_path / "cases"
    d.mkdir()
    for n in ("labels_v3.jsonl", "fresh_v1.jsonl", "fresh_v2.jsonl", "synthetic_robust_v1.jsonl"):
        shutil.copy(REAL / n, d / n)
    monkeypatch.setattr(compare, "CASES", d)
    return d


def _rewrite(path, fn):
    rows = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in fn(rows)), encoding="utf-8")


def test_real_inputs_load(cases_dir):
    s = compare.load_cases()
    assert {k: len(v) for k, v in s.items()} == {"tuning": 5, "dev": 12, "final_seen": 14, "holdout2": 24,
                                                 "synthetic_robust": 10}


def test_missing_label_file_fails(cases_dir):
    (cases_dir / "fresh_v1.jsonl").unlink()
    with pytest.raises(compare.IntegrityError, match="missing"):
        compare.load_cases()


def test_changed_frozen_labels_fail(cases_dir):
    _rewrite(cases_dir / "labels_v3.jsonl", lambda rows: rows[:-1])
    with pytest.raises(compare.IntegrityError, match="labels_v3.jsonl changed"):
        compare.load_cases()


def test_changed_fresh_set_fails(cases_dir):
    _rewrite(cases_dir / "fresh_v1.jsonl", lambda rows: [{**rows[0], "expected": {**rows[0]["expected"], "recommended": True}}] + rows[1:])
    with pytest.raises(compare.IntegrityError, match="fresh_v1.jsonl changed"):
        compare.load_cases()


def test_duplicate_case_ids_fail(cases_dir):
    _rewrite(cases_dir / "synthetic_robust_v1.jsonl", lambda rows: rows + [rows[0]])
    with pytest.raises(compare.IntegrityError, match="duplicate case IDs"):
        compare.load_cases()


def test_wrong_label_version_fails(cases_dir):
    _rewrite(cases_dir / "synthetic_robust_v1.jsonl", lambda rows: [{**r, "label_version": "x"} for r in rows])
    with pytest.raises(compare.IntegrityError, match="label_version"):
        compare.load_cases()


def test_holdout_contamination_fails(cases_dir, monkeypatch):
    """A holdout2 prompt reused in another split is contamination (pin bypassed to reach the check)."""
    def poison(rows):
        first = next(i for i, r in enumerate(rows) if r["split"] == "holdout2")
        return [{**r, "prompt_id": "kasparro:ai_shortlisting:001"} if i == first else r for i, r in enumerate(rows)]
    _rewrite(cases_dir / "fresh_v1.jsonl", poison)
    monkeypatch.setattr(compare, "_fresh_pin", lambda _v="fresh-v1": compare._sha(cases_dir / "fresh_v1.jsonl"))
    with pytest.raises(compare.IntegrityError, match="shares prompts"):
        compare.load_cases()


def test_wilson_interval_reference():
    assert compare.wilson(0, 0) is None
    lo, hi = compare.wilson(2, 7)
    assert 0.08 <= lo <= 0.09 and 0.64 <= hi <= 0.65


def test_fresh_v2_labels_load_with_the_same_splits(cases_dir):
    s1, s2 = compare.load_cases(), compare.load_cases("fresh-v2")
    assert {k: len(v) for k, v in s1.items()} == {k: len(v) for k, v in s2.items()}
    assert {c["label_version"] for c in s2["holdout2"]} == {"fresh-v2"}
