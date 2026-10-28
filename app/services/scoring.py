"""Deterministic visibility scoring and aggregation (vis-v1). No model is involved here.

Per-response score, 0-100, for SUCCEEDED analyses only:
    inclusion            +40  Kasparro is named in the answer body
    recommendation       +40  presented as a suitable option (implies inclusion)
    first_party_citation +20  the engine cited a kasparro.com URL
    negative             -30  unfavourable characterisation
    entity_confusion     -20  confused with / misidentified as another entity
    score = clamp(sum, 0, 100)
Reading: 0 = observed absence; 40 = named, neutral; 80 = recommended; 100 = recommended
and first-party cited with no negative or confusion.

Failed and skipped responses get score None. They are excluded from rate and mean
denominators and reported as coverage (succeeded / eligible), never counted as zero.
Recommendation position is recorded but not scored in v1, because explicit rankings
that include Kasparro are rarely observable in this snapshot.
"""
from __future__ import annotations

import math
from collections import defaultdict

SCORE_VERSION = "vis-v1"
WEIGHTS = {
    "inclusion": 40,
    "recommendation": 40,
    "first_party_citation": 20,
    "negative": -30,
    "entity_confusion": -20,
}


def components(labels: dict, citations: dict) -> dict[str, int]:
    return {
        "inclusion": WEIGHTS["inclusion"] if labels["mentioned"] else 0,
        "recommendation": WEIGHTS["recommendation"] if labels["recommended"] else 0,
        "first_party_citation": WEIGHTS["first_party_citation"] if citations["first_party_cited"] else 0,
        "negative": WEIGHTS["negative"] if labels["negative"] else 0,
        "entity_confusion": WEIGHTS["entity_confusion"] if labels["entity_confusion"] else 0,
    }


def score(comp: dict[str, int]) -> int:
    return max(0, min(100, sum(comp.values())))


def wilson(k: int, n: int, z: float = 1.96) -> list[float] | None:
    """95% Wilson score interval for a rate; None when the denominator is 0."""
    if n == 0:
        return None
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return [round(max(0.0, centre - half), 3), round(min(1.0, centre + half), 3)]


def _rate(k: int, n: int) -> dict:
    return {"count": k, "denominator": n, "rate": round(k / n, 3) if n else None, "ci95": wilson(k, n)}


def summarise(rows: list[dict]) -> dict:
    """rows: response_results rows as dicts with status, labels (dict|None),
    citations (dict|None), score (number|None)."""
    eligible = len(rows)
    ok = [r for r in rows if r["status"] == "succeeded"]
    n = len(ok)
    lab = lambda key: sum(1 for r in ok if r["labels"]["labels"][key])  # noqa: E731
    return {
        "eligible": eligible,
        "succeeded": n,
        "failed": sum(1 for r in rows if r["status"] == "failed"),
        "skipped": sum(1 for r in rows if r["status"] == "skipped"),
        "coverage": _rate(n, eligible),
        "mentioned": _rate(lab("mentioned"), n),
        "recommended": _rate(lab("recommended"), n),
        "negative": _rate(lab("negative"), n),
        "entity_confusion": _rate(lab("entity_confusion"), n),
        "first_party_cited": _rate(sum(1 for r in ok if r["citations"]["first_party_cited"]), n),
        "mean_score": round(sum(r["score"] for r in ok) / n, 1) if n else None,
    }


def aggregate(rows: list[dict]) -> dict:
    """Summaries overall and by engine x branded, engine x topic, plus a same-prompt
    comparison restricted to prompts where every engine succeeded."""
    groups: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(list))
    for r in rows:
        seg = "branded" if r["branded"] else "unbranded"
        groups["by_engine"][r["engine"]].append(r)
        groups["by_segment"][seg].append(r)
        groups["by_engine_segment"][f"{r['engine']}|{seg}"].append(r)
        groups["by_segment_topic"][f"{seg}|{r['category']}"].append(r)
    out = {"overall": summarise(rows)}
    for gname, buckets in groups.items():
        out[gname] = {k: summarise(v) for k, v in sorted(buckets.items())}

    by_prompt: dict[str, dict[str, dict]] = defaultdict(dict)
    for r in rows:
        by_prompt[r["prompt_id"]][r["engine"]] = r
    engines = sorted({r["engine"] for r in rows})
    complete = {p: e for p, e in by_prompt.items()
                if len(e) == len(engines) and all(x["status"] == "succeeded" for x in e.values())}
    patterns: dict[str, int] = defaultdict(int)
    for p, e in complete.items():
        key = "+".join(eng for eng in engines if e[eng]["labels"]["labels"]["mentioned"]) or "none"
        patterns[key] += 1
    out["paired_prompts"] = {
        "engines": engines,
        "prompts_total": len(by_prompt),
        "prompts_all_engines_succeeded": len(complete),
        "mention_patterns": dict(sorted(patterns.items())),
        "note": "Each prompt counted once by which engines mentioned Kasparro; "
                "prompts with any failed/skipped engine are excluded.",
    }
    return out
