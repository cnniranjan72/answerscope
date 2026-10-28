"""Citation counting policy (citation-v1).

* occurrences: every supplied citation row counts once (inline and source-panel rows are
  separate occurrences, as returned by the engine).
* distinct URLs: per response, URLs are normalised (lower-case host, 'www.' removed,
  fragment removed - this includes '#:~:text=' highlights - tracking parameters removed,
  trailing '/' removed) and counted once.
* first-party: host is kasparro.com or a subdomain. Other URLs containing 'kasparro'
  (LinkedIn page, job boards) are counted separately as 'brand-related third-party'.
* support: no cited page was opened, so every citation's claim support is 'unverified'.
"""
from __future__ import annotations

from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

CITATION_POLICY_VERSION = "citation-v1"
FIRST_PARTY_HOST = "kasparro.com"
_TRACKING_PREFIXES = ("utm_", "srsltid", "gclid", "fbclid", "mc_", "ref_src")


def host_of(url: str) -> str:
    host = urlsplit(url.strip()).netloc.lower().split("@")[-1].split(":")[0]
    return host[4:] if host.startswith("www.") else host


def normalise_url(url: str) -> str:
    parts = urlsplit(url.strip())
    query = urlencode([(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
                       if not k.lower().startswith(_TRACKING_PREFIXES)])
    path = parts.path.rstrip("/")
    return urlunsplit((parts.scheme.lower(), host_of(url), path, query, ""))


def is_first_party(host: str) -> bool:
    return host == FIRST_PARTY_HOST or host.endswith("." + FIRST_PARTY_HOST)


def citation_features(rows: list[dict]) -> dict:
    """rows: citation records for one response (dicts with url/citation_type)."""
    distinct = {}
    for r in rows:
        distinct.setdefault(normalise_url(r["url"]), host_of(r["url"]))
    first_party = sorted(u for u, h in distinct.items() if is_first_party(h))
    related = sorted(u for u, h in distinct.items() if not is_first_party(h) and "kasparro" in u.lower())
    return {
        "policy_version": CITATION_POLICY_VERSION,
        "occurrences": len(rows),
        "inline_occurrences": sum(1 for r in rows if r["citation_type"] == "inline_hyperlink"),
        "panel_occurrences": sum(1 for r in rows if r["citation_type"] == "sources_panel"),
        "distinct_urls": len(distinct),
        "first_party_cited": bool(first_party),
        "first_party_urls": first_party,
        "brand_related_third_party_urls": related,
        "support_status": "unverified",
    }
