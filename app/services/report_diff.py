"""Compare two report versions: what a reviewer needs before approving a re-run.

The comparison is descriptive. It separates a method change (prompt, score, category,
report generator, model or execution mode) from a data change (analysis and capture),
and marks each rate difference by whether the two 95% Wilson intervals overlap. Overlap
means the difference is within sampling uncertainty; non-overlap is a conservative sign of
a real difference *for the same method*. When the method changed, a rate difference
reflects the method at least as much as the engines, and the output says so.
"""
from __future__ import annotations

METHOD_FIELDS = ("prompt_version", "score_version", "category_version", "report_generator", "model",
                 "execution_mode", "citation_policy")
DATA_FIELDS = ("analysis_id", "historical_capture_date")
RATE_LABELS = ("mentioned", "recommended", "negative", "entity_confusion", "first_party_cited")
SCOPES = (("overall", ("overall",)), ("branded", ("by_segment", "branded")), ("unbranded", ("by_segment", "unbranded")))


def _get(d: dict, path: tuple[str, ...]) -> dict | None:
    for k in path:
        d = (d or {}).get(k)
    return d


def _frac(cell: dict | None) -> str | None:
    return f"{cell['count']}/{cell['denominator']}" if cell else None


def compare_contents(base: dict, other: dict) -> dict:
    pb, po = base.get("provenance", {}), other.get("provenance", {})
    method = [{"field": f, "base": pb.get(f), "other": po.get(f)} for f in METHOD_FIELDS if pb.get(f) != po.get(f)]
    data = [{"field": f, "base": pb.get(f), "other": po.get(f)} for f in DATA_FIELDS if pb.get(f) != po.get(f)]
    rates = []
    for scope, path in SCOPES:
        cb, co = _get(base.get("scorecard", {}), path), _get(other.get("scorecard", {}), path)
        if not cb or not co:
            continue
        for label in RATE_LABELS:
            a, b = cb.get(label), co.get(label)
            if not a or not b:
                continue
            if a["rate"] is None or b["rate"] is None:  # no successful answers on one side: nothing to compare
                rates.append({"kind": "rate", "scope": scope, "label": label, "base": _frac(a), "other": _frac(b),
                              "change_pp": None, "ci_overlap": None})
                continue
            overlap = a["ci95"][0] <= b["ci95"][1] and b["ci95"][0] <= a["ci95"][1]
            rates.append({"kind": "rate", "scope": scope, "label": label, "base": _frac(a), "other": _frac(b),
                          "change_pp": round(100 * (b["rate"] - a["rate"]), 1), "ci_overlap": overlap})
        rates.append({"kind": "info", "scope": scope, "label": "mean_score", "base": cb.get("mean_score"),
                      "other": co.get("mean_score"), "change_pp": None, "ci_overlap": None})
        rates.append({"kind": "info", "scope": scope, "label": "succeeded", "base": f"{cb.get('succeeded')}/{cb.get('eligible')}",
                      "other": f"{co.get('succeeded')}/{co.get('eligible')}", "change_pp": None, "ci_overlap": None})

    def diags(c):
        return {(d.get("metrics") or {}).get("pattern") or d["id"]: d for d in c.get("diagnostics", [])}

    db, do = diags(base), diags(other)
    diagnostics = {
        "in_both": [{"pattern": k, "base": f"{db[k]['id']} {db[k]['title']}", "other": f"{do[k]['id']} {do[k]['title']}"}
                    for k in db if k in do],
        "only_in_base": [f"{v['id']} {v['title']}" for k, v in db.items() if k not in do],
        "only_in_other": [f"{v['id']} {v['title']}" for k, v in do.items() if k not in db],
    }
    eb = {e["response_id"] for d in base.get("diagnostics", []) for e in d.get("evidence", [])}
    eo = {e["response_id"] for d in other.get("diagnostics", []) for e in d.get("evidence", [])}
    if method:
        reading = ("The method changed (" + ", ".join(m["field"] for m in method) + "), so rate differences mainly "
                   "reflect the method, not a change in the engines' answers"
                   + (" (same capture)." if not any(d["field"] == "historical_capture_date" for d in data) else "."))
    elif data:
        reading = ("Same method, different data: differences whose intervals do not overlap are candidates for a "
                   "real change; overlapping ones are within sampling uncertainty.")
    else:
        reading = "Same method and same data: any difference comes from editing, not from the analysis."
    return {"method_changes": method, "data_changes": data, "reading": reading, "rates": rates,
            "diagnostics": diagnostics,
            "evidence_responses": {"base": len(eb), "other": len(eo), "shared": len(eb & eo)}}


def to_markdown(diff: dict, base_label: str, other_label: str) -> str:
    L = [f"# Report comparison: {base_label} → {other_label}", "", f"**Reading:** {diff['reading']}", ""]
    if diff["method_changes"] or diff["data_changes"]:
        L += ["| Changed | Base | Other |", "|---|---|---|"]
        L += [f"| {c['field']} | {c['base']} | {c['other']} |" for c in diff["method_changes"] + diff["data_changes"]]
        L.append("")
    L += ["| Scope | Measure | Base | Other | Change (pp) | 95% intervals |", "|---|---|---|---|---|---|"]
    for r in diff["rates"]:
        ci = ("not comparable (no successful answers)" if r["kind"] == "rate" and r["ci_overlap"] is None else
              "" if r["ci_overlap"] is None else "overlap" if r["ci_overlap"] else "**do not overlap**")
        ch = "" if r["change_pp"] is None else f"{r['change_pp']:+.1f}"
        L.append(f"| {r['scope']} | {r['label']} | {r['base']} | {r['other']} | {ch} | {ci} |")
    d = diff["diagnostics"]
    L += ["", "**Diagnostics**", ""]
    L += [f"- in both: {x['base']} → {x['other']}" for x in d["in_both"]]
    L += [f"- only in base: {x}" for x in d["only_in_base"]]
    L += [f"- only in other: {x}" for x in d["only_in_other"]]
    e = diff["evidence_responses"]
    L += ["", f"Diagnostic evidence cites {e['base']} responses in the base and {e['other']} in the other; "
              f"{e['shared']} are shared.", ""]
    return "\n".join(L)
