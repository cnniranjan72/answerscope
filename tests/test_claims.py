"""claims-v1: possible product misattribution is flagged for the reviewer, never counted."""
from __future__ import annotations

import pytest

from app.services.claims import PRICE, price_claims
from tests.conftest import A


@pytest.mark.parametrize("text,found", [
    ("starts at ₹49,999.", ["₹49,999"]), ("costs $499/month.", ["$499"]), ("50,000 INR", ["50,000 INR"]),
    ("$10k budget", ["$10k"]), ("Rs. 25,000 per audit", ["Rs. 25,000"]), ("$2.5 per seat", ["$2.5"]),
    ("brands ($10M-$100M+)", []), ("$1.5M ARR", []), ("$5 million", []), ("$100+ brands", []), ("₹2 crore", []),
])
def test_price_pattern_excludes_revenue_magnitudes(text, found):
    assert [m.group(0) for m in PRICE.finditer(text)] == found


def test_h06_like_claim_cited_only_to_another_domain_is_flagged():
    body = ("Based on pricing information, **Kasparro's 14-day AI Revenue Diagnostic starts at ₹49,999**. "
            "[www.revenuepulseai.com](https://www.revenuepulseai.com/?utm_source=chatgpt.com)\n\nOther text.")
    [c] = price_claims(body)
    assert c["price"] == "₹49,999" and c["cited_only_to"] == ["revenuepulseai.com"]
    assert "revenuepulseai.com)" not in c["excerpt"]


@pytest.mark.parametrize("body", [
    "Kasparro costs $499/month [pricing](https://kasparro.com/pricing).",          # first-party source
    "Kasparro costs $499/month [a](https://kasparro.com/p) [b](https://other.io/x).",  # first-party among others
    "Kasparro costs $499/month.",                                                   # no inline source to compare
    "Profound costs $499/month [p](https://other.io/x).\n\nKasparro is new.",       # price is not in a Kasparro paragraph
])
def test_supported_or_unrelated_prices_are_not_flagged(body):
    assert price_claims(body) == []


def test_report_view_carries_advisories_outside_the_hashed_content(client, report):
    r = client.get(f"/reports/{report['report_id']}", headers=A).json()
    assert r["claim_advisories"]["version"] == "claims-v1" and isinstance(r["claim_advisories"]["items"], list)
    assert "claim_advisories" not in r["latest"]["content"]


def test_health_reports_every_version_a_deploy_check_needs(client):
    v = client.get("/health").json()["versions"]
    assert v == {"prompt": "classify-v2", "score": "vis-v1", "category": "cat-v1", "citation_policy": v["citation_policy"],
                 "report_generator": "report-v3", "evidence_policy": "evidence-v3", "claim_check": "claims-v1"}
    assert v["citation_policy"]
