"""Report comparison: method vs data changes, and interval overlap on rate changes."""
from __future__ import annotations

import copy

from app.services.report_diff import compare_contents
from tests.conftest import A, R
from tests.test_review import decide, submit


def cell(count, den, lo, hi):
    return {"count": count, "denominator": den, "rate": count / den, "ci95": [lo, hi]}


def content(prompt, rec, analysis="a1"):
    seg = {"recommended": rec, "succeeded": 74, "eligible": 75, "mean_score": 30.0}
    return {"provenance": {"prompt_version": prompt, "analysis_id": analysis, "historical_capture_date": "2026-07-31"},
            "scorecard": {"overall": seg, "by_segment": {"branded": seg}},
            "diagnostics": [{"id": "D1", "title": "Gap", "metrics": {"pattern": "unbranded_gap"},
                             "evidence": [{"response_id": "r1", "quote": "q"}]}]}


def test_method_change_is_named_and_non_overlapping_intervals_are_marked():
    base = content("classify-v1", cell(40, 73, 0.43, 0.66), "a1")
    other = content("classify-v2", cell(12, 74, 0.09, 0.26), "a2")
    d = compare_contents(base, other)
    assert [m["field"] for m in d["method_changes"]] == ["prompt_version"]
    assert "method changed" in d["reading"] and "same capture" in d["reading"]
    rec = next(r for r in d["rates"] if r["scope"] == "overall" and r["label"] == "recommended")
    assert rec["base"] == "40/73" and rec["other"] == "12/74" and rec["ci_overlap"] is False
    assert rec["change_pp"] == round(100 * (12 / 74 - 40 / 73), 1)


def test_same_method_new_data_reads_overlap_as_uncertainty():
    base = content("classify-v2", cell(12, 74, 0.09, 0.26), "a1")
    other = content("classify-v2", cell(15, 74, 0.12, 0.30), "a2")
    d = compare_contents(base, other)
    assert not d["method_changes"] and "Same method, different data" in d["reading"]
    assert next(r for r in d["rates"] if r["label"] == "recommended")["ci_overlap"] is True


def test_identical_content_has_no_changes_and_diagnostics_are_matched_by_pattern():
    base = content("classify-v2", cell(12, 74, 0.09, 0.26))
    other = copy.deepcopy(base)
    other["diagnostics"].append({"id": "D2", "title": "New", "metrics": {"pattern": "entity_confusion"}, "evidence": []})
    d = compare_contents(base, other)
    assert not d["method_changes"] and not d["data_changes"] and "editing" in d["reading"]
    assert d["diagnostics"]["only_in_other"] == ["D2 New"] and len(d["diagnostics"]["in_both"]) == 1


def test_compare_endpoint_uses_the_approved_version_and_needs_a_token(client, report, analysed):
    rid = report["report_id"]
    assert submit(client, rid, 1).status_code == 200
    assert decide(client, rid, 1).status_code == 200
    other = client.post("/reports", headers=A, json={"analysis_id": analysed}).json()["report_id"]
    assert client.get(f"/reports/{other}/compare", params={"against": rid}).status_code == 401
    r = client.get(f"/reports/{other}/compare", params={"against": rid}, headers=R)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["base"]["status"] == "approved" and body["other"]["status"] == "draft"
    assert not body["method_changes"] and "# Report comparison" in body["markdown"]
    assert client.get(f"/reports/{other}/compare", params={"against": "nope"}, headers=R).status_code == 404


def test_a_segment_without_successful_answers_is_not_comparable_rather_than_an_error():
    empty = {"count": 0, "denominator": 0, "rate": None, "ci95": None}
    base = content("classify-v2", empty, "a1")
    other = content("classify-v2", cell(12, 74, 0.09, 0.26), "a2")
    d = compare_contents(base, other)
    rec = next(r for r in d["rates"] if r["label"] == "recommended")
    assert rec["kind"] == "rate" and rec["ci_overlap"] is None and rec["change_pp"] is None
    from app.services.report_diff import to_markdown
    assert "not comparable" in to_markdown(d, "a", "b")
