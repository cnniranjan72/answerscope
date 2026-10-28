"""Scoring invariants and arithmetic, checked against hand-computed values."""
import pytest

from app.services import scoring
from app.services.citations import citation_features, normalise_url

L = lambda **k: {"mentioned": False, "recommended": False, "negative": False, "entity_confusion": False, **k}  # noqa
C = lambda fp: {"first_party_cited": fp}  # noqa


@pytest.mark.parametrize("labels,fp,expected", [
    (L(), False, 0),
    (L(mentioned=True), False, 40),
    (L(mentioned=True), True, 60),
    (L(mentioned=True, recommended=True), False, 80),
    (L(mentioned=True, recommended=True), True, 100),
    (L(mentioned=True, negative=True), False, 10),
    (L(mentioned=True, recommended=True, negative=True), True, 70),
    (L(mentioned=True, negative=True, entity_confusion=True), False, 0),  # clamped from -10
    (L(entity_confusion=True), False, 0),
])
def test_score_table(labels, fp, expected):
    assert scoring.score(scoring.components(labels, C(fp))) == expected


def test_score_bounds_exhaustive():
    import itertools
    for m, r, n, e, f in itertools.product([False, True], repeat=5):
        s = scoring.score(scoring.components(L(mentioned=m, recommended=r, negative=n, entity_confusion=e), C(f)))
        assert 0 <= s <= 100


def _row(engine, status, mentioned=False, score=None, prompt="p1", branded=True):
    labels = {"labels": L(mentioned=mentioned)} if status == "succeeded" else None
    return {"engine": engine, "status": status, "labels": labels, "citations": {"first_party_cited": False},
            "score": score, "prompt_id": prompt, "branded": branded, "category": "x"}


def test_summary_denominators_exclude_failures():
    """Brief example: 12 attempted, 2 failed, 4 of 10 valid mention the brand."""
    rows = ([_row("chatgpt", "succeeded", True, 40)] * 4 + [_row("chatgpt", "succeeded", False, 0)] * 6
            + [_row("chatgpt", "failed")] * 2)
    s = scoring.summarise(rows)
    assert (s["eligible"], s["succeeded"], s["failed"]) == (12, 10, 2)
    assert s["mentioned"]["count"] == 4 and s["mentioned"]["denominator"] == 10
    assert s["coverage"]["count"] == 10 and s["coverage"]["denominator"] == 12
    assert s["mean_score"] == 16.0


def test_empty_denominator_gives_none_not_zero():
    s = scoring.summarise([_row("gemini", "failed")])
    assert s["mentioned"]["rate"] is None and s["mean_score"] is None


def test_wilson_reference_values():
    assert scoring.wilson(0, 0) is None
    assert scoring.wilson(4, 10) == [0.168, 0.687]


def test_paired_comparison_only_complete_prompts():
    rows = [_row("aimode", "succeeded", True, 40, "p1"), _row("chatgpt", "succeeded", True, 40, "p1"),
            _row("aimode", "succeeded", False, 0, "p2"), _row("chatgpt", "failed", prompt="p2")]
    p = scoring.aggregate(rows)["paired_prompts"]
    assert p["prompts_all_engines_succeeded"] == 1 and p["mention_patterns"] == {"aimode+chatgpt": 1}


def test_citation_policy():
    assert normalise_url("https://WWW.Example.com/a/?utm_source=x&id=2#:~:text=hi") == "https://example.com/a?id=2"
    f = citation_features([
        {"url": "https://kasparro.com/", "citation_type": "inline_hyperlink"},
        {"url": "https://www.kasparro.com", "citation_type": "sources_panel"},
        {"url": "https://www.linkedin.com/company/kasparro-ai", "citation_type": "sources_panel"},
    ])
    assert f["occurrences"] == 3 and f["distinct_urls"] == 2
    assert f["first_party_cited"] and f["brand_related_third_party_urls"] == ["https://linkedin.com/company/kasparro-ai"]
    assert f["support_status"] == "unverified"
