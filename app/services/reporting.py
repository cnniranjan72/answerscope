"""Draft report generation (report-v1) and evidence verification.

Diagnostics are computed deterministically from the stored analysis results. Each
candidate pattern is counted with its denominator, ranked by
    priority = affected responses x severity weight,
and the top three become the draft diagnostics, each with one remedy. Every quote
comes from a verified evidence span of a succeeded result. The analyst may then edit
the text. verify_content() re-checks every quote against the source answers, so an
edited or invented quote blocks submission.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from collections import Counter, defaultdict

from app.db import utcnow
from app.services import scoring
from app.services.analysis import get_run, result_rows
from app.services.citations import CITATION_POLICY_VERSION
from app.services.text import answer_body, locate

REPORT_SCHEMA_VERSION = "report-v1"
SEVERITY = {"unbranded_gap": 1.0, "entity_confusion": 1.0, "credibility_gap": 0.8, "branded_win": 0.6}
MAX_EVIDENCE = 6
BRAND_SNAPSHOT_ID = "BRAND-SNAPSHOT-20260731"


def canonical(content: dict) -> str:
    return json.dumps(content, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _pick_evidence(rows: list[dict], label: str, limit: int = MAX_EVIDENCE) -> list[dict]:
    """Round-robin across engines so evidence is not drawn from a single engine."""
    by_engine: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        spans = r["labels"]["evidence"].get(label) or []
        if spans:
            by_engine[r["engine"]].append({"response_id": r["response_id"], "quote": spans[0]["quote"]})
    out: list[dict] = []
    while len(out) < limit and any(by_engine.values()):
        for eng in sorted(by_engine):
            if by_engine[eng] and len(out) < limit:
                out.append(by_engine[eng].pop(0))
    return out


def _by_engine(rows: list[dict], label: str) -> dict:
    out = {}
    for eng in sorted({r["engine"] for r in rows}):
        sub = [r for r in rows if r["engine"] == eng]
        out[eng] = f"{sum(1 for r in sub if r['labels']['labels'][label])}/{len(sub)}"
    return out


def _candidates(conn: sqlite3.Connection, rows: list[dict]) -> list[dict]:
    ok = [r for r in rows if r["status"] == "succeeded"]
    branded = [r for r in ok if r["branded"]]
    unbranded = [r for r in ok if not r["branded"]]
    cands = []

    if unbranded:
        absent = [r for r in unbranded if not r["labels"]["labels"]["mentioned"]]
        comp = Counter(c["name"].lower() for r in unbranded for c in r["labels"]["competitors"])
        display: dict[str, str] = {}
        ev: list[dict] = []
        used: set[str] = set()
        for name, _ in comp.most_common(10):  # one quote per top competitor, distinct responses
            hit = next(((r, c) for r in unbranded if r["response_id"] not in used
                        for c in r["labels"]["competitors"] if c["name"].lower() == name and c["evidence"]), None)
            if hit and len(ev) < MAX_EVIDENCE:
                r, c = hit
                display[name] = c["name"]
                ev.append({"response_id": r["response_id"], "quote": c["evidence"]["quote"]})
                used.add(r["response_id"])
        hosts = Counter()
        for r in unbranded:
            for row in conn.execute("SELECT DISTINCT host FROM citations WHERE response_id = ?", (r["response_id"],)):
                hosts[row["host"]] += 1
        b_mention = sum(1 for r in branded if r["labels"]["labels"]["mentioned"])
        top_comp = ", ".join(f"{display.get(n, n)} ({k})" for n, k in comp.most_common(6))
        top_hosts = ", ".join(f"{h} ({k})" for h, k in hosts.most_common(6))
        cands.append({
            "key": "unbranded_gap", "kind": "loss", "affected": len(absent),
            "title": "Kasparro is absent from unbranded discovery answers",
            "observation": (
                f"In unbranded questions (the asker does not name Kasparro), Kasparro was named in "
                f"{len(unbranded) - len(absent)}/{len(unbranded)} successfully analysed answers "
                f"(by engine: {_by_engine(unbranded, 'mentioned')}), versus {b_mention}/{len(branded)} branded answers. "
                f"Competitors named most often in unbranded answers (number of answers): {top_comp or 'none extracted'}."),
            "hypothesis": (
                "Engines build category answers from third-party lists, reviews and comparison content; Kasparro may be "
                "absent from the sources engines retrieve for these questions. Recency may also matter: the archived "
                "homepage schema gives a 2026 foundingDate. This is a hypothesis, not established by the snapshot."),
            "how_to_test": (
                f"Check whether the hosts most cited in unbranded answers mention Kasparro at all "
                f"(most cited, number of answers: {top_hosts}). If none do, the absence is consistent with the "
                f"hypothesis; if several do and Kasparro is still omitted, look for another cause."),
            "metrics": {"unbranded_mentioned": f"{len(unbranded) - len(absent)}/{len(unbranded)}",
                        "branded_mentioned": f"{b_mention}/{len(branded)}",
                        "top_competitors_unbranded": dict(comp.most_common(8)),
                        "top_cited_hosts_unbranded": dict(hosts.most_common(8))},
            "evidence": ev,
        })

    if branded:
        conf = [r for r in branded if r["labels"]["labels"]["entity_confusion"]]
        cands.append({
            "key": "entity_confusion", "kind": "risk", "affected": len(conf),
            "title": "Engines confuse Kasparro with other entities (notably Kaspr)",
            "observation": (
                f"{len(conf)}/{len(branded)} branded answers confuse or misidentify Kasparro "
                f"(by engine: {_by_engine(branded, 'entity_confusion')}). Some answers describe a different product "
                f"instead of Kasparro."),
            "hypothesis": (
                "The name is close to an established product (Kaspr), and the entity signals engines can retrieve for "
                "Kasparro may be weak. The archived homepage Organization schema "
                f"({BRAND_SNAPSHOT_ID}) has no sameAs links to other profiles. Unverified as a cause."),
            "how_to_test": (
                "Re-run the branded prompts with the fuller name and domain ('Kasparro (kasparro.com)'). If confusion "
                "disappears, the problem is name ambiguity. Separately audit which pages engines cite when they confuse "
                "the name."),
            "metrics": {"confused": f"{len(conf)}/{len(branded)}", "by_engine": _by_engine(branded, "entity_confusion")},
            "evidence": _pick_evidence(conf, "entity_confusion"),
        })

        neg = [r for r in branded if r["labels"]["labels"]["negative"]]
        cands.append({
            "key": "credibility_gap", "kind": "loss", "affected": len(neg),
            "title": "Branded answers question Kasparro's track record and recognition",
            "observation": (
                f"{len(neg)}/{len(branded)} branded answers characterise Kasparro unfavourably "
                f"(by engine: {_by_engine(branded, 'negative')}), typically citing no independent evidence, reviews or "
                f"recognition, or comparing it unfavourably with a named competitor."),
            "hypothesis": (
                "Engines find few independent, verifiable sources about Kasparro (reviews, case studies, third-party "
                "coverage), so they hedge. Citations were not opened, so their support for these claims is unverified."),
            "how_to_test": (
                "List the citations attached to the negative answers and classify each source as first-party, "
                "job listing, independent review, or unrelated. A low share of independent sources supports the "
                "hypothesis."),
            "metrics": {"negative": f"{len(neg)}/{len(branded)}", "by_engine": _by_engine(branded, "negative")},
            "evidence": _pick_evidence(neg, "negative"),
        })

        rec = [r for r in branded if r["labels"]["labels"]["recommended"]]
        cands.append({
            "key": "branded_win", "kind": "win", "affected": len(rec),
            "title": "When asked about Kasparro directly, some engines present it as a fit",
            "observation": (
                f"{len(rec)}/{len(branded)} branded answers present Kasparro as a suitable option "
                f"(by engine: {_by_engine(branded, 'recommended')})."),
            "hypothesis": "First-party pages are retrievable and describe the offer clearly enough to be repeated.",
            "how_to_test": "Compare the cited sources in recommending vs non-recommending branded answers.",
            "metrics": {"recommended": f"{len(rec)}/{len(branded)}", "by_engine": _by_engine(branded, "recommended")},
            "evidence": _pick_evidence(rec, "recommended"),
        })

    for c in cands:
        c["priority_score"] = round(c["affected"] * SEVERITY[c["key"]], 2)
    return sorted([c for c in cands if c["evidence"]], key=lambda c: -c["priority_score"])


REMEDY_TEMPLATES = {
    "unbranded_gap": dict(
        action=("Investigation first: for each of the most-cited hosts in unbranded answers, record whether Kasparro "
                "is listed, and whether a factual listing or comparison inclusion is possible through legitimate "
                "editorial routes. Do not create spam or undisclosed promotional content."),
        expected_benefit=("Identifies whether the discovery gap has an addressable source-coverage cause before any "
                          "spend. Inclusion is not guaranteed even if coverage improves."),
        effort="medium", effort_detail="About 1-2 analyst days for the source audit; outreach effort unknown.",
        uncertainty=("High. One snapshot per prompt and engine; no causal evidence links source coverage to "
                     "inclusion, and engines differ in retrieval."),
        validation=("Re-run the same unbranded prompts on the same three engines with the same settings (India, en). "
                    "Primary metric: unbranded mention rate (baseline {unbranded_mentioned}). Secondary: number of "
                    "top-cited hosts that mention Kasparro. Use at least 3 repeated runs before claiming change.")),
    "entity_confusion": dict(
        action=("Audit entity signals: confirm that the brand name, one-line description and domain are consistent "
                "across owned pages and profiles, and evaluate adding schema.org sameAs links to official profiles in "
                "the Organization markup. Separately test the prompt-wording hypothesis described in the diagnostic."),
        expected_benefit=("Less risk that buyers asking about Kasparro receive information about a different "
                          "company (pricing, cancellation and self-serve answers were about Kaspr)."),
        effort="low", effort_detail="Hours for the audit and markup review; deployment is out of scope here.",
        uncertainty=("Medium-high. Google states no special schema is required for AI features, and markup alone "
                     "does not guarantee disambiguation."),
        validation=("Re-run the branded prompts and measure the entity-confusion rate (baseline {confused}) "
                    "per engine, over at least 3 runs.")),
    "credibility_gap": dict(
        action=("Inventory which verifiable proof exists (methodology documentation, pricing pages, case studies "
                "with customer permission, independent reviews) and which is missing. Publish only claims that can be "
                "substantiated; do not invent outcomes."),
        expected_benefit=("Gives engines and buyers checkable sources, which may reduce 'no independent evidence' "
                          "hedging. Recognition cannot be manufactured quickly."),
        effort="high", effort_detail="Weeks: depends on customer permissions and third-party coverage.",
        uncertainty=("High. Negative framing may persist until independent coverage exists; citation support was not "
                     "verified in this analysis."),
        validation=("Re-run the branded prompts; measure the negative-characterisation rate (baseline {negative}) and "
                    "the share of answers citing independent sources, over at least 3 runs.")),
    "branded_win": dict(
        action=("Identify which first-party pages are cited in recommending answers and keep them accurate and "
                "accessible to search crawlers (check robots rules for OAI-SearchBot and Googlebot)."),
        expected_benefit="Protects the current branded representation; it does not address discovery.",
        effort="low", effort_detail="Hours.",
        uncertainty="Medium. Correlation between cited pages and recommendation is not causal.",
        validation="Track the branded recommendation rate (baseline {recommended}) in repeated runs."),
}


def build_draft(conn: sqlite3.Connection, analysis_id: str) -> dict:
    run = get_run(conn, analysis_id)
    rows = result_rows(conn, analysis_id)
    agg = scoring.aggregate(rows)
    cands = _candidates(conn, rows)[:3]
    diagnostics, remedies = [], []
    for i, c in enumerate(cands, start=1):
        diagnostics.append({"id": f"D{i}", "priority": i, "title": c["title"], "kind": c["kind"],
                            "observation": c["observation"], "hypothesis": c["hypothesis"],
                            "how_to_test": c["how_to_test"], "metrics": {**c["metrics"],
                            "priority_score": c["priority_score"], "pattern": c["key"]},
                            "evidence": c["evidence"]})
        t = REMEDY_TEMPLATES[c["key"]]
        fmt = {k: v for k, v in c["metrics"].items() if isinstance(v, str)}
        fmt.update({"unbranded_mentioned": fmt.get("unbranded_mentioned", "n/a"), "confused": fmt.get("confused", "n/a"),
                    "negative": fmt.get("negative", "n/a"), "recommended": fmt.get("recommended", "n/a")})
        remedies.append({"id": f"R{i}", "priority": i, "diagnostic_id": f"D{i}",
                         "problem": c["title"] + ". " + c["observation"].split(". ")[0] + ".",
                         "evidence": c["evidence"][:3], "action": t["action"],
                         "expected_benefit": t["expected_benefit"], "effort": t["effort"],
                         "effort_detail": t["effort_detail"], "uncertainty": t["uncertainty"],
                         "validation": t["validation"].format(**fmt)})
    o = agg["overall"]
    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "title": "Kasparro AI visibility snapshot (captured 31 July 2026)",
        "executive_summary": (
            f"{o['succeeded']}/{o['eligible']} archived answers were analysed successfully ({o['failed']} failed, "
            f"{o['skipped']} skipped). Kasparro was named in {agg['by_segment'].get('branded', {}).get('mentioned', {}).get('count', 0)}"
            f"/{agg['by_segment'].get('branded', {}).get('succeeded', 0)} branded and "
            f"{agg['by_segment'].get('unbranded', {}).get('mentioned', {}).get('count', 0)}"
            f"/{agg['by_segment'].get('unbranded', {}).get('succeeded', 0)} unbranded answers. This is one historical "
            f"snapshot (India, English, one answer per prompt and engine), not a current ranking."),
        "provenance": {"analysis_id": analysis_id, "execution_mode": run["execution_mode"], "model": run["model"],
                       "model_quality_note": run["model_quality_note"], "prompt_version": run["prompt_version"],
                       "score_version": run["score_version"], "category_version": run["category_version"],
                       "citation_policy": CITATION_POLICY_VERSION, "report_generator": REPORT_SCHEMA_VERSION,
                       "historical_capture_date": "2026-07-31", "generated_at": utcnow()},
        "scorecard": agg,
        "score_definition": {"version": scoring.SCORE_VERSION, "weights": scoring.WEIGHTS, "scale": "0-100, clamped",
                             "failed_or_skipped": "excluded from rates and means; reported as coverage"},
        "diagnostics": diagnostics,
        "remedies": remedies,
        "limitations": [
            "One captured answer per prompt and engine: a snapshot, not a stable ranking.",
            "Citation support is unverified: no cited page was opened.",
            "Prompt categories are rule-based (cat-v1) and inferred from question wording.",
            "Labels depend on one model run; see the evaluation report for measured agreement.",
        ],
        "analyst_notes": "",
    }


def verify_content(conn: sqlite3.Connection, content: dict, *, for_submit: bool) -> list[str]:
    """Return problems; empty means every quote is found verbatim in its cited response
    and every remedy follows from an existing diagnostic's evidence."""
    problems: list[str] = []
    bodies: dict[str, str | None] = {}

    def body_of(rid: str) -> str | None:
        if rid not in bodies:
            row = conn.execute("SELECT answer_text FROM responses WHERE response_id = ?", (rid,)).fetchone()
            bodies[rid] = answer_body(row["answer_text"]) if row else None
        return bodies[rid]

    def check(where: str, ev: list[dict]):
        for e in ev:
            b = body_of(e["response_id"])
            if b is None:
                problems.append(f"{where}: unknown response_id {e['response_id']}")
            elif locate(e["quote"], b) is None:
                problems.append(f"{where}: quote not found in response {e['response_id']}: {e['quote'][:80]!r}")

    diags = {d["id"]: d for d in content.get("diagnostics", [])}
    for d in content.get("diagnostics", []):
        if not d.get("evidence"):
            problems.append(f"{d['id']}: no evidence")
        check(d["id"], d.get("evidence", []))
    for r in content.get("remedies", []):
        check(r["id"], r.get("evidence", []))
        d = diags.get(r["diagnostic_id"])
        if d is None:
            problems.append(f"{r['id']}: refers to missing diagnostic {r['diagnostic_id']}")
            continue
        dq = {(e["response_id"], e["quote"]) for e in d["evidence"]}
        for e in r.get("evidence", []):
            if (e["response_id"], e["quote"]) not in dq:
                problems.append(f"{r['id']}: evidence not drawn from its diagnostic {d['id']}")
    if for_submit:
        for kind, items in (("diagnostics", content.get("diagnostics", [])), ("remedies", content.get("remedies", []))):
            if len(items) != 3:
                problems.append(f"exactly 3 {kind} are required for submission (found {len(items)})")
            if sorted(i["priority"] for i in items) != list(range(1, len(items) + 1)):
                problems.append(f"{kind} priorities must be 1..{len(items)} without gaps")
            if len({i["id"] for i in items}) != len(items):
                problems.append(f"{kind} ids must be unique")
    return problems


def enrich_evidence(conn: sqlite3.Connection, content: dict) -> dict:
    """For export: attach engine, prompt and exact character offsets to every quote."""
    out = json.loads(json.dumps(content))
    meta = {}
    for section in ("diagnostics", "remedies"):
        for item in out.get(section, []):
            for e in item.get("evidence", []):
                rid = e["response_id"]
                if rid not in meta:
                    row = conn.execute("SELECT r.engine, r.prompt_id, r.answer_text, p.text FROM responses r "
                                       "JOIN prompts p USING (prompt_id) WHERE response_id = ?", (rid,)).fetchone()
                    meta[rid] = row
                row = meta[rid]
                loc = locate(e["quote"], answer_body(row["answer_text"]))
                e.update({"engine": row["engine"], "prompt_id": row["prompt_id"], "question": row["text"],
                          "location": {"field": "answer_text", "start": loc[0], "end": loc[1]} if loc else None})
    return out

