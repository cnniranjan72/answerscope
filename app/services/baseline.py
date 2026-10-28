"""Rule-based baseline classifier (baseline-v1).

Deliberately simple keyword rules over sentences that name the brand. It is the
comparison point for the model-based classifier and the default output of the
engineering stub. It returns the same JSON contract as the model.
"""
from __future__ import annotations

import json
import re

from app.services.text import BRAND_RE, URL_RE

BASELINE_VERSION = "baseline-v1"

KNOWN_VENDORS = [
    "Profound", "Peec AI", "Otterly.AI", "Otterly", "AthenaHQ", "Dageno AI", "Dageno", "Semrush",
    "Ahrefs", "Scrunch AI", "Scrunch", "BrightEdge", "Conductor", "Goodie", "Evertune", "Rankscale",
    "Writesonic", "HubSpot", "Frase", "Gauge", "ZipTie", "Siftly", "Omnia", "AirOps", "Alhena",
    "Searchable", "SE Ranking", "Similarweb", "LLMrefs", "Trakkr", "Brandlight", "Cairrot", "Bluefish",
]
_RECOMMEND = re.compile(
    r"\b(yes|can help|designed (specifically )?for|good (choice|fit|option)|recommended?|"
    r"well[- ]suited|strong (choice|option|fit)|worth (considering|it)|ideal for|built for)\b", re.I)
_NEGATIVE = re.compile(
    r"(not (a )?widely (recognized|recognised|known)|no (direct |specific |public(ly available)? )?"
    r"(evidence|data|information|reviews|testimonials)|couldn'?t (find|verify|identify)|"
    r"not (yet )?(as )?(established|proven)|lean toward|superior to|less (proven|established|mature)|"
    r"\black(s|ing)?\b|missing|skeptic|isn'?t much independent)", re.I)
_KASPR = re.compile(r"\bkaspr\b", re.I)
_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+|\n+")


def _sentences(body: str) -> list[str]:
    return [s.strip() for s in _SENT_SPLIT.split(body) if len(s.strip()) > 3]


def classify(body: str) -> dict:
    # Quotes must be verbatim source sentences; URLs are removed only for matching
    # (regression: failure F2, quotes built from URL-stripped text were unverifiable).
    sents = [s[:500] for s in _sentences(body)]
    clean = {s: URL_RE.sub(" ", s) for s in sents}
    brand_sents = [s for s in sents if BRAND_RE.search(clean[s])]
    rec = [s for s in brand_sents if _RECOMMEND.search(clean[s]) and not _NEGATIVE.search(clean[s])]
    neg = [s for s in brand_sents if _NEGATIVE.search(clean[s])]
    confusion = [s for s in sents if _KASPR.search(clean[s])]
    text_wo_urls = URL_RE.sub(" ", body)
    competitors = []
    seen = set()
    for name in KNOWN_VENDORS:
        m = re.search(r"\b" + re.escape(name) + r"\b", text_wo_urls, re.I)
        if m and not any(name.lower() in s for s in seen):
            seen.add(name.lower())
            ev = next((s for s in sents if m.group(0) in clean[s]), None)
            if ev:
                competitors.append({"name": m.group(0), "evidence": ev})
    mentioned = bool(brand_sents)
    return {
        "kasparro_mentioned": mentioned,
        "mention_evidence": brand_sents[:1],
        "kasparro_recommended": bool(rec),
        "recommendation_evidence": rec[:2],
        "negative_characterization": bool(neg),
        "negative_evidence": neg[:2],
        "entity_confusion": bool(confusion),
        "confusion_evidence": confusion[:1],
        "competitors": competitors[:15],
        "kasparro_list_position": None,
        "position_basis": "prose_only" if mentioned else "not_mentioned",
        "rationale": f"{BASELINE_VERSION} keyword rules",
    }


def classify_json(body: str) -> str:
    return json.dumps(classify(body))
