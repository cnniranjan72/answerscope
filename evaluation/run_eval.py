"""Evaluation runner: one command, readable report.

  python -m evaluation.run_eval                      # model outputs from replay (keyless)
  python -m evaluation.run_eval --provider ollama    # real local model (add --record to refresh replay)

Compares the rule-based baseline with the model-based classifier on the same labelled
cases, keeps tuning cases separate from the final check (holdout + synthetic), verifies
score arithmetic against hand-computed values, and checks report diagnostics for
evidence support, including a deliberately corrupted report that must be caught.
Writes evaluation/results/eval_results.json and evaluation/results/eval_report.md.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
import sys
import tempfile
from collections import defaultdict
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.config import load_settings  # noqa: E402
from app.db import connect, init_db  # noqa: E402
from app.services import baseline, scoring  # noqa: E402
from app.services.analysis import build_provider, result_rows, run_analysis  # noqa: E402
from app.services.analyzer import PROMPT_VERSION, AnalysisOutcome, analyse_response, validate_output  # noqa: E402
from app.services.citations import citation_features  # noqa: E402
from app.services.ingestion import import_records, load_pack  # noqa: E402
from app.services.llm import OllamaProvider  # noqa: E402
from app.services.reporting import build_draft, verify_content  # noqa: E402
from app.services.text import answer_body  # noqa: E402

CASES = ROOT / "evaluation" / "cases" / "labels_v3.jsonl"  # candidate-reviewed 2026-10-29; v1, v2 kept for history
OUT = ROOT / "evaluation" / "results"
LABELS = ["mentioned", "recommended", "negative", "entity_confusion"]
PATTERN_LABEL = {"entity_confusion": "entity_confusion", "credibility_gap": "negative", "branded_win": "recommended"}


def norm_name(name: str) -> str:
    n = re.sub(r"[^a-z0-9]", "", name.lower())
    return n[:-2] if n.endswith("ai") and len(n) > 4 else n


def name_match(a: str, b: str) -> bool:
    x, y = norm_name(a), norm_name(b)
    return bool(x) and bool(y) and (x.startswith(y) or y.startswith(x))


def load_inputs(case: dict, pack: dict) -> tuple[str, str, bool]:
    if case.get("synthetic"):
        return case["question"], case["answer_text"], False
    r = pack["responses"][case["response_id"]]
    feats = citation_features(pack["citations"].get(case["response_id"], []))
    return pack["prompts"][r["prompt_id"]], answer_body(r["answer_text"]), feats["first_party_cited"]


def run_system(name: str, cases: list[dict], pack: dict, provider=None, record_dir: Path | None = None,
               max_attempts: int = 3) -> dict:
    out = {}
    for c in cases:
        q, body, fp = load_inputs(c, pack)
        key = c["response_id"] or c["case_id"]
        if name == "baseline":
            try:
                v = validate_output(baseline.classify_json(body), body)
                res = AnalysisOutcome("succeeded", None, v)
            except Exception as e:  # baseline output is validated like the model's
                res = AnalysisOutcome("failed", f"baseline output rejected: {e}", None)
        else:
            res = analyse_response(provider, response_id=key, question=q, body=body, max_attempts=max_attempts)
            if record_dir is not None and isinstance(provider, OllamaProvider):
                from app.services.analysis import _write_recording
                _write_recording(record_dir, key, provider.model, res)
        pred = None
        if res.status == "succeeded":
            comp = scoring.components(res.labels["labels"], {"first_party_cited": fp})
            pred = {"labels": {k: res.labels["labels"][k] for k in LABELS},
                    "competitors": [x["name"] for x in res.labels["competitors"]],
                    "position": res.labels["position"], "score": scoring.score(comp),
                    "rationale": res.labels.get("rationale")}
        out[c["case_id"]] = {"status": res.status, "reason": res.reason, "attempts": len(res.attempts), "pred": pred}
    return out


def metrics(cases: list[dict], preds: dict, exclude_ambiguous: bool) -> dict:
    by_label = {}
    for lab in LABELS:
        tp = fp = fn = tn = 0
        for c in cases:
            p = preds[c["case_id"]]["pred"]
            if p is None or (exclude_ambiguous and lab in c["ambiguous_labels"]):
                continue
            e, g = c["expected"][lab], p["labels"][lab]
            tp += e and g
            fp += (not e) and g
            fn += e and (not g)
            tn += (not e) and (not g)
        n = tp + fp + fn + tn
        prec = tp / (tp + fp) if tp + fp else None
        rec = tp / (tp + fn) if tp + fn else None
        by_label[lab] = {"tp": tp, "fp": fp, "fn": fn, "tn": tn, "n": n,
                         "precision": _r(prec), "recall": _r(rec),
                         "f1": _r(2 * prec * rec / (prec + rec)) if prec and rec else (0.0 if prec == 0 or rec == 0 else None),
                         "agreement": _r((tp + tn) / n) if n else None}
    return by_label


def competitor_metrics(cases, preds) -> dict:
    tp = fp = fn = 0
    for c in cases:
        p = preds[c["case_id"]]["pred"]
        if p is None:
            continue
        exp, opt = c["competitors"], c["competitors_optional"]
        for name in p["competitors"]:
            if any(name_match(name, e) for e in exp):
                tp += 1
            elif not any(name_match(name, o) for o in opt):
                fp += 1
        fn += sum(1 for e in exp if not any(name_match(e, n) for n in p["competitors"]))
    return {"tp": tp, "fp": fp, "fn": fn, "precision": _r(tp / (tp + fp)) if tp + fp else None,
            "recall": _r(tp / (tp + fn)) if tp + fn else None}


def score_metrics(cases, preds) -> dict:
    diffs = [abs(preds[c["case_id"]]["pred"]["score"] - c["expected_score"]) for c in cases
             if preds[c["case_id"]]["pred"]]
    pos = [(c["position"], preds[c["case_id"]]["pred"]["position"]) for c in cases
           if c["position"] is not None and preds[c["case_id"]]["pred"]]
    return {"n": len(diffs), "exact": sum(1 for d in diffs if d == 0),
            "mae": _r(sum(diffs) / len(diffs)) if diffs else None,
            "position_cases": len(pos), "position_exact": sum(1 for e, g in pos if e == g)}


def counts(cases, preds) -> dict:
    st = [preds[c["case_id"]]["status"] for c in cases]
    return {"eligible": len(st), "succeeded": st.count("succeeded"), "failed": st.count("failed"),
            "skipped": st.count("skipped")}


def _r(x):
    return None if x is None else round(x, 3)


def arithmetic_check(cases) -> dict:
    """Independent check: hand-computed expected_score vs the scoring module applied to the
    expected labels. A mismatch means the formula implementation and its spec disagree."""
    rows = []
    for c in cases:
        got = scoring.score(scoring.components(c["expected"], {"first_party_cited": c["first_party_cited"]}))
        rows.append({"case_id": c["case_id"], "hand_computed": c["expected_score"], "module": got,
                     "ok": got == c["expected_score"]})
    return {"checked": len(rows), "mismatches": [r for r in rows if not r["ok"]]}


def diagnostics_check(provider_name: str, settings) -> dict:
    """Full pack -> analysis -> draft report; verify evidence and label consistency, then
    corrupt a copy and confirm each injected defect is detected."""
    with tempfile.TemporaryDirectory() as tmp:
        s = replace(settings, db_path=Path(tmp) / "eval.db")
        init_db(s.db_path)
        conn = connect(s.db_path)
        try:
            import_records(conn, load_pack(s.pack_dir), actor="eval", source="configured_pack")
            provider = build_provider(provider_name, s)
            aid = run_analysis(conn, s, provider, actor="eval")
            rows = {r["response_id"]: r for r in result_rows(conn, aid)}
            summary = scoring.aggregate(list(rows.values()))["overall"]
            draft = build_draft(conn, aid)
            problems = verify_content(conn, draft, for_submit=True) + label_consistency(draft, rows)

            bad = copy.deepcopy(draft)
            injected = []
            if bad["diagnostics"]:
                d0 = bad["diagnostics"][0]
                d0["evidence"].append({"response_id": d0["evidence"][0]["response_id"],
                                       "quote": "Kasparro is the most trusted AI visibility platform in India."})
                injected.append("unsupported claim: fabricated quote")
                other = next((r for r in rows if r != d0["evidence"][0]["response_id"]), None)
                d0["evidence"].append({"response_id": other, "quote": d0["evidence"][0]["quote"]})
                injected.append("incorrect evidence: real quote attributed to the wrong response")
            if bad["remedies"]:
                bad["remedies"][0]["diagnostic_id"] = "D9"
                injected.append("remedy that follows from no diagnostic")
            if len(bad["diagnostics"]) > 1 and bad["remedies"][1:]:
                bad["remedies"][1]["evidence"] = [bad["diagnostics"][0]["evidence"][0]]
                injected.append("remedy evidence not drawn from its diagnostic")
            caught = verify_content(conn, bad, for_submit=True)
            return {"provider": provider_name, "execution_mode": provider.execution_mode,
                    "analysis_counts": {k: summary[k] for k in ("eligible", "succeeded", "failed", "skipped")},
                    "diagnostics": [{"id": d["id"], "title": d["title"], "pattern": d["metrics"]["pattern"],
                                     "evidence_items": len(d["evidence"])} for d in draft["diagnostics"]],
                    "clean_report_problems": problems,
                    "negative_case": {"injected": injected, "detected": caught,
                                      "all_detected": len(caught) >= len(injected)}}
        finally:
            conn.close()


def label_consistency(draft: dict, rows: dict) -> list[str]:
    """Each evidence item must come from a succeeded response carrying the label its
    diagnostic claims (e.g. a confusion diagnostic cites confused answers)."""
    problems = []
    for d in draft["diagnostics"]:
        pattern = d["metrics"].get("pattern")
        for e in d["evidence"]:
            r = rows.get(e["response_id"])
            if r is None or r["status"] != "succeeded":
                problems.append(f"{d['id']}: evidence {e['response_id']} has no successful analysis")
            elif pattern == "unbranded_gap" and (r["branded"] or r["labels"]["labels"]["mentioned"]):
                problems.append(f"{d['id']}: evidence {e['response_id']} is not an unbranded absence")
            elif pattern in PATTERN_LABEL and not r["labels"]["labels"][PATTERN_LABEL[pattern]]:
                problems.append(f"{d['id']}: evidence {e['response_id']} lacks label {PATTERN_LABEL[pattern]}")
    return problems


def load_pack_index(pack_dir: Path) -> dict:
    raw = load_pack(pack_dir)
    cites = defaultdict(list)
    for c in raw["citations"]:
        cites[c["response_id"]].append(c)
    return {"prompts": {p["prompt_id"]: p["text"] for p in raw["prompts"]},
            "responses": {r["response_id"]: r for r in raw["responses"]}, "citations": cites}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m evaluation.run_eval")
    ap.add_argument("--provider", default="replay", choices=["replay", "ollama", "stub"])
    ap.add_argument("--record", action="store_true")
    ap.add_argument("--labels", default=str(CASES), help="label file (default: candidate-reviewed labels_v3.jsonl)")
    ap.add_argument("--report-provider", default="replay", choices=["replay", "stub", "skip"],
                    help="provider for the full-pack diagnostics check")
    args = ap.parse_args(argv)

    settings = load_settings()
    cases = [json.loads(l) for l in Path(args.labels).read_text(encoding="utf-8").splitlines() if l.strip()]
    pack = load_pack_index(settings.pack_dir)
    provider = build_provider(args.provider, settings)
    record_dir = settings.replay_dir / PROMPT_VERSION.replace("-", "_") if args.record else None

    systems = {"baseline": run_system("baseline", cases, pack),
               "model": run_system("model", cases, pack, provider, record_dir, settings.model_max_attempts)}
    splits = {"final": [c for c in cases if c["split"] in ("holdout", "synthetic")],
              "tuning": [c for c in cases if c["split"] == "tuning"]}
    excluded = [c["case_id"] for c in splits["final"] if (c.get("review") or {}).get("sensitivity_exclude")]
    if excluded:  # sensitivity view: final split without cases affected by post-hoc validator changes
        splits["final_sensitivity"] = [c for c in splits["final"] if c["case_id"] not in excluded]
    results = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "label_version": cases[0]["label_version"], "prompt_version": PROMPT_VERSION,
        "score_version": scoring.SCORE_VERSION, "baseline_version": baseline.BASELINE_VERSION,
        "model": {"provider": args.provider, "execution_mode": provider.execution_mode, "model": provider.model},
        "arithmetic": arithmetic_check(cases),
        "splits": {},
        "cases": {cid: {"expected": next(c for c in cases if c["case_id"] == cid)["expected"],
                        **{s: systems[s][cid] for s in systems}} for cid in (c["case_id"] for c in cases)},
    }
    for split, cs in splits.items():
        results["splits"][split] = {
            "n_cases": len(cs), "case_ids": [c["case_id"] for c in cs],
            **{s: {"counts": counts(cs, systems[s]),
                   "labels_strict": metrics(cs, systems[s], exclude_ambiguous=False),
                   "labels_unambiguous": metrics(cs, systems[s], exclude_ambiguous=True),
                   "competitors": competitor_metrics(cs, systems[s]),
                   "score": score_metrics(cs, systems[s])} for s in systems}}
    if args.report_provider != "skip":
        results["diagnostics_check"] = diagnostics_check(args.report_provider, settings)

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "eval_results.json").write_text(json.dumps(results, indent=1, ensure_ascii=False), encoding="utf-8")
    (OUT / "eval_report.md").write_text(render(results, cases), encoding="utf-8")
    f = results["splits"]["final"]
    print(f"final check ({f['n_cases']} cases): baseline {f['baseline']['counts']} | model {f['model']['counts']}")
    print(f"wrote {OUT / 'eval_report.md'}")
    return 0


def _fmt(x):
    return "n/a" if x is None else f"{x:.2f}" if isinstance(x, float) else str(x)


def render(res: dict, cases: list[dict]) -> str:
    m = res["model"]
    lines = [
        "# Evaluation report", "",
        f"Generated {res['generated_at']} | labels `{res['label_version']}` | prompt `{res['prompt_version']}` | "
        f"score `{res['score_version']}` | baseline `{res['baseline_version']}`", "",
        f"**Model system:** provider `{m['provider']}`, execution mode `{m['execution_mode']}`, model `{m['model']}`.",
    ]
    if m["execution_mode"] == "stub":
        lines += ["", "> STUB MODE: the 'model' column is the deterministic baseline. Model quality is NOT measured."]
    elif m["execution_mode"] == "replay":
        lines += ["", "> Replay mode: recorded outputs from one earlier local-model run are re-validated by current "
                  "code. This reproduces that run; it does not measure run-to-run variance."]
    lines += ["", "Final check = holdout + synthetic cases (never used for prompt tuning). Tuning cases are reported "
              "separately and should not be read as generalisation.", ""]
    for split in [k for k in ("final", "final_sensitivity", "tuning") if k in res["splits"]]:
        s = res["splits"][split]
        lines += [f"## {split.title()} split ({s['n_cases']} cases: {', '.join(s['case_ids'])})", "",
                  "| System | Eligible | Succeeded | Failed | Skipped |", "|---|---|---|---|---|"]
        for sys_ in ("baseline", "model"):
            c = s[sys_]["counts"]
            lines.append(f"| {sys_} | {c['eligible']} | {c['succeeded']} | {c['failed']} | {c['skipped']} |")
        for mode, title in (("labels_strict", "all labels"), ("labels_unambiguous", "ambiguous labels excluded")):
            lines += ["", f"**Per-label metrics ({title})**", "",
                      "| Label | System | Positives | TP | FP | FN | TN | Precision | Recall | F1 | Agreement |",
                      "|---|---|---|---|---|---|---|---|---|---|---|"]
            for lab in LABELS:
                for sys_ in ("baseline", "model"):
                    x = s[sys_][mode][lab]
                    lines.append(f"| {lab} | {sys_} | {x['tp'] + x['fn']} | {x['tp']} | {x['fp']} | {x['fn']} | {x['tn']} | "
                                 f"{_fmt(x['precision'])} | {_fmt(x['recall'])} | {_fmt(x['f1'])} | {_fmt(x['agreement'])} |")
        lines += ["", "| System | Competitor precision | Competitor recall | Score exact | Score MAE | Position exact |",
                  "|---|---|---|---|---|---|"]
        for sys_ in ("baseline", "model"):
            cm, sm = s[sys_]["competitors"], s[sys_]["score"]
            lines.append(f"| {sys_} | {_fmt(cm['precision'])} (tp {cm['tp']}, fp {cm['fp']}) | {_fmt(cm['recall'])} "
                         f"(fn {cm['fn']}) | {sm['exact']}/{sm['n']} | {_fmt(sm['mae'])} | "
                         f"{sm['position_exact']}/{sm['position_cases']} |")
        lines.append("")
    lines += ["## Per-case disagreements with expected labels", "",
              "| Case | Split | System | Status | Label differences | Score (pred/exp) |", "|---|---|---|---|---|---|"]
    byid = {c["case_id"]: c for c in cases}
    for cid, row in res["cases"].items():
        c = byid[cid]
        for sys_ in ("baseline", "model"):
            r = row[sys_]
            if r["pred"] is None:
                lines.append(f"| {cid} | {c['split']} | {sys_} | {r['status']} | {(r['reason'] or '')[:90]} | - |")
                continue
            diffs = [f"{lab}: exp {c['expected'][lab]}, got {r['pred']['labels'][lab]}"
                     + (" (ambiguous)" if lab in c["ambiguous_labels"] else "")
                     for lab in LABELS if r["pred"]["labels"][lab] != c["expected"][lab]]
            if diffs or r["pred"]["score"] != c["expected_score"]:
                lines.append(f"| {cid} | {c['split']} | {sys_} | {r['status']} | {'; '.join(diffs) or '-'} | "
                             f"{r['pred']['score']}/{c['expected_score']} |")
    a = res["arithmetic"]
    lines += ["", "## Score arithmetic (independent check)", "",
              f"Hand-computed expected scores vs `scoring.score()` on expected labels: {a['checked']} checked, "
              f"{len(a['mismatches'])} mismatches.", ""]
    d = res.get("diagnostics_check")
    if d:
        lines += ["## Diagnostic and remedy evidence checks", "",
                  f"Full-pack analysis via `{d['provider']}` ({d['execution_mode']}): {d['analysis_counts']}.", ""]
        for x in d["diagnostics"]:
            lines.append(f"- {x['id']} ({x['pattern']}): {x['title']} - {x['evidence_items']} evidence items")
        lines += ["", f"Problems in the generated report (quotes verbatim in cited response, remedy follows from its "
                  f"diagnostic, evidence carries the claimed label): **{len(d['clean_report_problems'])}**"]
        lines += [f"  - {p}" for p in d["clean_report_problems"][:20]]
        n = d["negative_case"]
        lines += ["", f"Negative case: injected {len(n['injected'])} defects; checker reported {len(n['detected'])} "
                  f"problems; all detected: **{n['all_detected']}**"]
        lines += [f"  - injected: {i}" for i in n["injected"]] + [f"  - detected: {p}" for p in n["detected"]]
    lines += ["", "## Limits of this evaluation", "",
              "- 17 real + 2 synthetic cases: metrics have wide uncertainty; one label flip moves precision/recall a lot.",
              "- Labels were drafted by the AI coding assistant from full answer text and need candidate review; a single "
              "labeller means no inter-annotator agreement.",
              "- 'Recommended' is the most ambiguous label; ambiguous labels are reported both included and excluded.",
              "- One model run only; replay reproduces it but cannot show variance. Citation support is not evaluated.",
              "- The checker verifies that evidence exists and carries the claimed label; it cannot judge whether a "
              "hypothesis is correct. No LLM grades its own output here."]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
