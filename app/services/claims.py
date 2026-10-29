"""claims-v1: flag possible product misattribution (failure mode FM5, case H06) for the reviewer.

A paragraph that names Kasparro and states a price, but whose inline citations all point to
domains other than kasparro.com, may attribute another company's offer to Kasparro (H06:
a diagnostic priced in INR, cited only to revenuepulseai.com). This is an advisory for a
human: it never changes labels, scores or report content, and it is not counted in any
diagnostic. Paragraphs without inline links are not flagged (no source to compare).

Measured on the 31 Jul 2026 pack (29 Oct 2026): 3 of 75 branded answers state a Kasparro
price; 2 are flagged (H06, the labelled misattribution, and one unlabelled deal-size claim
cited only to a job site); the third has no inline link. The sample is too small to report
precision or recall.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from app.services.citations import is_first_party
from app.services.text import BRAND_RE

CLAIM_CHECK_VERSION = "claims-v1"
# A price: currency + amount (optionally "k"), or amount + currency code. Revenue magnitudes
# ("$10M-$100M+", "$5 million", "₹2 crore") are client sizes, not prices, and are excluded.
PRICE = re.compile(r"(?:(?:₹|\$|€|£|\bUSD|\bINR|\bRs\.?)\s?\d[\d,]*(?:\.\d+)?k?|\b\d[\d,]*(?:\.\d+)?\s?(?:USD|INR)\b)"
                   r"(?![\d,]|\.\d|\s?(?:[mb]n?|million|billion|crore|lakh|cr)\b|[mb]n?-|\+)", re.I)
INLINE_LINK = re.compile(r"\]\((https?://[^)\s]+)\)")
_PARAGRAPH = re.compile(r"\n\s*\n|\n(?=\s*(?:[-*+]|\d+[.)])\s)")


def price_claims(body: str) -> list[dict]:
    """Paragraphs naming Kasparro with a price whose inline links are all non-Kasparro."""
    out = []
    for para in _PARAGRAPH.split(body):
        if not (BRAND_RE.search(para) and (m := PRICE.search(para))):
            continue
        hosts = sorted({(urlparse(u).hostname or "").removeprefix("www.") for u in INLINE_LINK.findall(para)} - {""})
        if hosts and not any(is_first_party(h) for h in hosts):
            out.append({"price": m.group(0), "cited_only_to": hosts,
                        "excerpt": " ".join(INLINE_LINK.sub("]", para).split())[:200]})
    return out
