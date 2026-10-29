"""Three-way comparison: keyword baseline vs classify-v1 vs classify-v2.

classify-v2 was the candidate when this report was produced and became the production default
on 29 Oct 2026 (DECISION_NOTE.md, promotion record); classify-v1 produced the approved report.

  python -m evaluation.compare                       # v1 and v2 from replay recordings (keyless)
  python -m evaluation.compare --v2-provider ollama --record --splits dev,tuning   # tune v2 live
  python -m evaluation.compare --from-predictions evaluation/results/compare_predictions.json
  python -m evaluation.compare --fresh fresh-v2     # same, on the candidate-decided fresh labels
                                                    # (writes compare_fresh_v2_*; fresh-v1 stays the default)

Splits and what they can show:
  tuning     5 labels-v3 cases used to write classify-v1 (and to check classify-v2).
  dev        12 fresh-v1 cases used to tune classify-v2.
  final_seen 14 labels-v3 holdout + synthetic cases. Their classify-v1 errors were read while
             designing classify-v2, so for v2 they are NOT an independent test.
  holdout2   24 fresh-v1 cases, labelled and hash-frozen before classify-v2 ran on them, from
             prompts disjoint from all other splits: the independent test of v2 (and of v1).
  synthetic_robust  10 SYNTHETIC one-per-failure-mode fixtures. Robustness checks only, written
             after the failure analysis; never pooled with real-answer results.

Fails loudly on: missing pack or labels, duplicate case IDs, unexpected label versions,
changed frozen label files, and split contamination. Writes compare_report.md,
compare_results.json and compare_predictions.json; --from-predictions recomputes every
metric from saved predictions and checks it matches the saved results.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections import Counter
from pathlib import Path

from app.config import load_settings
from app.services import baseline, scoring
from app.services.analysis import _write_recording, build_provider, replay_dir
from app.services.analyzer import AnalysisOutcome, analyse_response, validate_output
from app.services.llm import OllamaProvider
from evaluation.run_eval import LABELS, competitor_metrics, load_inputs, load_pack_index, metrics

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "evaluation" / "cases"
OUT = ROOT / "evaluation" / "results"
FROZEN = {"labels_v3.jsonl": "a893038eb00bd4c7"}  # sha256 prefix (LF-normalised); fresh-v1 is pinned in its test
SYSTEMS = ("baseline", "classify-v1", "classify-v2")
SPLIT_ORDER = ("tuning", "dev", "final_seen", "holdout2", "synthetic_robust")


class IntegrityError(RuntimeError):
    pass


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


FRESH = {"fresh-v1": ("fresh_v1.jsonl", "FRESH_SHA256"), "fresh-v2": ("fresh_v2.jsonl", "FRESH_V2_SHA256")}


def _fresh_pin(fresh: str = "fresh-v1") -> str:
    text = (ROOT / "tests" / "test_fresh_cases.py").read_text(encoding="utf-8")
    return text.split(f'{FRESH[fresh][1]} = "', 1)[1].split('"', 1)[0]


def load_cases(fresh_version: str = "fresh-v1") -> dict[str, list[dict]]:
    v3p, frp, srp = CASES / "labels_v3.jsonl", CASES / FRESH[fresh_version][0], CASES / "synthetic_robust_v1.jsonl"
    for p in (v3p, frp, srp):
        if not p.exists():
            raise IntegrityError(f"missing label file {p}")
    if not _sha(v3p).startswith(FROZEN["labels_v3.jsonl"]):
        raise IntegrityError("labels_v3.jsonl changed: frozen candidate-reviewed labels must not change")
    if _sha(frp) != _fresh_pin(fresh_version):
        raise IntegrityError(f"{frp.name} changed after it was frozen")
    load = lambda p: [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]  # noqa: E731
    v3, fresh, robust = load(v3p), load(frp), load(srp)
    if ({c["label_version"] for c in v3} != {"labels-v3"} or {c["label_version"] for c in fresh} != {fresh_version}
            or {c["label_version"] for c in robust} != {"synthetic-robust-v1"}):
        raise IntegrityError("unexpected label_version in a label file")
    splits = {"tuning": [c for c in v3 if c["split"] == "tuning"],
              "dev": [c for c in fresh if c["split"] == "dev"],
              "final_seen": [c for c in v3 if c["split"] in ("holdout", "synthetic")],
              "holdout2": [c for c in fresh if c["split"] == "holdout2"],
              "synthetic_robust": robust}
    ids = [c["case_id"] for cs in splits.values() for c in cs]
    if len(ids) != len(set(ids)):
        raise IntegrityError(f"duplicate case IDs: {[k for k, n in Counter(ids).items() if n > 1]}")
    rids = [c["response_id"] for cs in splits.values() for c in cs if c["response_id"]]
    if len(rids) != len(set(rids)):
        raise IntegrityError("the same response appears in two cases or splits")
    h2 = {c["prompt_id"] for c in splits["holdout2"]}
    other = {c["prompt_id"] for s in ("tuning", "dev", "final_seen") for c in splits[s]}
    if h2 & other:
        raise IntegrityError(f"holdout2 shares prompts with other splits: {sorted(h2 & other)}")
    return splits


def run(system: str, cases: list[dict], pack: dict, settings, provider=None, record_dir=None) -> dict:
    version = system if system.startswith("classify-") else None
    out = {}
    for c in cases:
        q, body, fp = load_inputs(c, pack)
        key = c["response_id"] or c["case_id"]
        if system == "baseline":
            try:
                res = AnalysisOutcome("succeeded", None, validate_output(baseline.classify_json(body), body,
                                                                       "classify-v1"))  # baseline emits the v1 contract
            except Exception as e:  # noqa: BLE001 - validated like the model's output
                res = AnalysisOutcome("failed", f"baseline output rejected: {e}", None)
        else:
            res = analyse_response(provider, response_id=key, question=q, body=body,
                                   max_attempts=settings.model_max_attempts, version=version)
            if record_dir is not None and isinstance(provider, OllamaProvider):
                _write_recording(record_dir, key, provider.model, res, version)
        pred = None
        if res.status == "succeeded":
            lab = res.labels
            pred = {"labels": {k: lab["labels"][k] for k in LABELS},
                    "recommendation_type": lab.get("recommendation_type"),
                    "recommendation_evidence": [e["quote"] for e in lab["evidence"]["recommended"]],
                    "competitors": [x["name"] for x in lab["competitors"]],
                    "score": scoring.score(scoring.components(lab["labels"], {"first_party_cited": fp}))}
        out[c["case_id"]] = {"status": res.status, "reason": res.reason, "attempts": len(res.attempts),
                             "pred": pred}
    return out


def _valid_recording(d: Path, case: dict, pack: dict, version: str) -> bool:
    """A recording exists and was made for exactly this prompt text and answer (input hash)."""
    from app.services.analyzer import build_messages, input_hash
    f = d / f"{case['response_id'] or case['case_id']}.json"
    if not f.exists():
        return False
    q, body, _ = load_inputs(case, pack)
    return json.loads(f.read_text(encoding="utf-8")).get("input_sha256") == input_hash(build_messages(q, body, version), version)


def wilson(k: int, n: int) -> list[float] | None:
    if not n:
        return None
    p, z = k / n, 1.96
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(c - h, 2), round(c + h, 2)]


def summarise(splits: dict, preds: dict) -> dict:
    res = {}
    for s in SPLIT_ORDER:
        cs = splits[s]
        res[s] = {"cases": [c["case_id"] for c in cs], "systems": {}}
        for sysname in SYSTEMS:
            p = preds[sysname]
            st = Counter(p[c["case_id"]]["status"] for c in cs)
            m_all, m_unamb = metrics(cs, p, False), metrics(cs, p, True)
            for m in (m_all, m_unamb):
                for v in m.values():
                    v["precision_ci95"] = wilson(v["tp"], v["tp"] + v["fp"])
                    v["recall_ci95"] = wilson(v["tp"], v["tp"] + v["fn"])
            errors = {lab: {"fp": [c["case_id"] for c in cs if p[c["case_id"]]["pred"]
                                   and p[c["case_id"]]["pred"]["labels"][lab] and not c["expected"][lab]],
                            "fn": [c["case_id"] for c in cs if p[c["case_id"]]["pred"]
                                   and not p[c["case_id"]]["pred"]["labels"][lab] and c["expected"][lab]]}
                      for lab in LABELS}
            scored = [abs(p[c["case_id"]]["pred"]["score"] - c["expected_score"]) for c in cs if p[c["case_id"]]["pred"]]
            res[s]["systems"][sysname] = {
                "counts": {"eligible": len(cs), "succeeded": st["succeeded"], "failed": st["failed"]},
                "failures": {c["case_id"]: p[c["case_id"]]["reason"] for c in cs if p[c["case_id"]]["status"] != "succeeded"},
                "labels_strict": m_all, "labels_unambiguous": m_unamb, "errors": errors,
                "competitors": competitor_metrics([c for c in cs if c["competitors"] is not None], p),
                "score_mae": round(sum(scored) / len(scored), 2) if scored else None,
                "score_exact": f"{sum(1 for d in scored if d == 0)}/{len(scored)}",
            }
        rt = Counter((p_["pred"] or {}).get("recommendation_type") for cid, p_ in preds["classify-v2"].items()
                     if cid in res[s]["cases"])
        res[s]["v2_recommendation_types"] = {str(k): v for k, v in rt.items()}
    return res


FRESH_NOTE = {"fresh-v1": "fresh-v1 (AI-drafted, blind to predictions, candidate review pending)",
              "fresh-v2": ("fresh-v2 (fresh-v1 after an AI audit; the candidate decided the 4 audit items, "
                           "changing D-017-aimode only; see fresh_review_log.jsonl)")}


def report(results: dict, provenance: dict) -> str:
    L = ["# Comparison report: baseline vs classify-v1 vs classify-v2", "",
         f"Generated {provenance['generated_at']} | labels {provenance['label_files']} | score `vis-v1` | "
         f"v1 `{provenance['providers']['classify-v1']}` | v2 `{provenance['providers']['classify-v2']}`", "",
         "> **Read holdout2 for independent evidence.** final_seen was inspected while designing classify-v2; "
         "dev was used to tune it. Labels: labels-v3 (candidate-reviewed) and " + FRESH_NOTE[provenance.get("fresh", "fresh-v1")] + ". Intervals are Wilson 95% on tiny counts: treat them as a "
         "warning about uncertainty, not as significance tests.", ""]
    for s in SPLIT_ORDER:
        r = results[s]
        L += [f"## {s} ({len(r['cases'])} cases)", "",
              "| System | Succeeded | Failed | Score exact | Score MAE |", "|---|---|---|---|---|"]
        for sysname in SYSTEMS:
            x = r["systems"][sysname]
            L.append(f"| {sysname} | {x['counts']['succeeded']} | {x['counts']['failed']} | {x['score_exact']} | {x['score_mae']} |")
        for mode, title in (("labels_strict", "all labels"), ("labels_unambiguous", "ambiguous labels excluded")):
            L += ["", f"**{title}** (TP/FP/FN/TN = confusion matrix; P and R with Wilson 95% interval)", "",
                  "| Label | System | Pos | TP | FP | FN | TN | Precision | Recall | F1 |", "|---|---|---|---|---|---|---|---|---|---|"]
            for lab in LABELS:
                for sysname in SYSTEMS:
                    m = r["systems"][sysname][mode][lab]
                    ci = lambda v, k: f"{v} {k}" if v is not None else "n/a"  # noqa: E731
                    pci = m["precision_ci95"] and f"[{m['precision_ci95'][0]}, {m['precision_ci95'][1]}]" or ""
                    rci = m["recall_ci95"] and f"[{m['recall_ci95'][0]}, {m['recall_ci95'][1]}]" or ""
                    L.append(f"| {lab} | {sysname} | {m['tp'] + m['fn']} | {m['tp']} | {m['fp']} | {m['fn']} | {m['tn']} | "
                             f"{ci(m['precision'], pci)} | {ci(m['recall'], rci)} | {m['f1'] if m['f1'] is not None else 'n/a'} |")
        L += ["", "**Errors by case (strict)**", "", "| Label | System | False positives | False negatives |", "|---|---|---|---|"]
        for lab in LABELS:
            for sysname in SYSTEMS:
                e = r["systems"][sysname]["errors"][lab]
                if e["fp"] or e["fn"]:
                    L.append(f"| {lab} | {sysname} | {', '.join(e['fp']) or '-'} | {', '.join(e['fn']) or '-'} |")
        fails = {k: v for sysname in SYSTEMS for k, v in r["systems"][sysname]["failures"].items()}
        if fails:
            L += ["", "**Failed analyses:** " + "; ".join(f"{k}: {v[:140]}" for k, v in fails.items())]
        L += ["", f"classify-v2 recommendation_type distribution: {r['v2_recommendation_types']}", ""]
    L += ["## Provenance", "", "```", json.dumps(provenance, indent=1), "```", ""]
    return "\n".join(L)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m evaluation.compare")
    ap.add_argument("--v2-provider", default="replay", choices=["replay", "ollama"])
    ap.add_argument("--record", action="store_true", help="with --v2-provider ollama: write classify-v2 recordings")
    ap.add_argument("--fill-v1", action="store_true",
                    help="record classify-v1 live (Ollama) only for cases with no valid v1 recording; "
                         "valid recordings are never touched")
    ap.add_argument("--fill-v2", action="store_true",
                    help="same for classify-v2 (a recording made for an older prompt text is re-recorded)")
    ap.add_argument("--splits", help=f"comma-separated subset of {','.join(SPLIT_ORDER)} (default: all)")
    ap.add_argument("--from-predictions", help="recompute metrics from saved predictions and verify them")
    ap.add_argument("--fresh", default="fresh-v1", choices=sorted(FRESH), help="fresh label version for dev/holdout2")
    args = ap.parse_args(argv)
    splits = load_cases(args.fresh)
    base = "compare" if args.fresh == "fresh-v1" else f"compare_{args.fresh.replace('-', '_')}"
    if args.from_predictions:
        saved = json.loads(Path(args.from_predictions).read_text(encoding="utf-8"))
        results = summarise(splits, saved["predictions"])
        stored = json.loads((OUT / f"{base}_results.json").read_text(encoding="utf-8"))["results"]
        if results != stored:
            raise IntegrityError(f"metrics recomputed from saved predictions differ from {base}_results.json")
        print(f"reproduced: metrics recomputed from saved predictions match {base}_results.json")
        return 0
    if args.splits:
        keep = set(args.splits.split(","))
        if not keep <= set(SPLIT_ORDER):
            ap.error(f"unknown split in {keep}")
        splits = {k: (v if k in keep else []) for k, v in splits.items()}
    settings = load_settings()
    if not settings.pack_dir.exists():
        raise IntegrityError(f"assignment pack not found at {settings.pack_dir}")
    pack = load_pack_index(settings.pack_dir)
    every = [c for s in SPLIT_ORDER for c in splits[s]]
    for version, wanted in (("classify-v1", args.fill_v1), ("classify-v2", args.fill_v2)):
        if wanted:
            d, live = replay_dir(settings, version), build_provider("ollama", settings, version=version)
            todo = [c for c in every if not _valid_recording(d, c, pack, version)]
            print(f"fill {version}: recording {len(todo)} cases without a valid recording", file=sys.stderr)
            run(version, todo, pack, settings, live, d)
    v1 = build_provider("replay", settings, version="classify-v1")
    v2 = build_provider(args.v2_provider, settings, version="classify-v2")
    rec = replay_dir(settings, "classify-v2") if args.record else None
    preds = {"baseline": run("baseline", every, pack, settings),
             "classify-v1": run("classify-v1", every, pack, settings, v1),
             "classify-v2": run("classify-v2", every, pack, settings, v2, rec)}
    results = summarise(splits, preds)
    from app.db import utcnow
    provenance = {"generated_at": utcnow(), "fresh": args.fresh,
                  "label_files": {n: _sha(CASES / n)[:16] for n in ("labels_v3.jsonl", FRESH[args.fresh][0])},
                  "providers": {"classify-v1": v1.execution_mode, "classify-v2": v2.execution_mode},
                  "model": v2.model, "baseline": "baseline-v1",
                  "prompt_files": {v: _sha(ROOT / "prompts" / f"{v.replace('-', '_')}.md")[:16]
                                   for v in ("classify-v1", "classify-v2")},
                  "splits_run": [s for s in SPLIT_ORDER if splits[s]]}
    OUT.mkdir(parents=True, exist_ok=True)
    full = not args.splits
    stem = base if full else f"{base}_partial"
    (OUT / f"{stem}_predictions.json").write_text(json.dumps({"predictions": preds}, indent=1, ensure_ascii=False), encoding="utf-8")
    (OUT / f"{stem}_results.json").write_text(json.dumps({"provenance": provenance, "results": results}, indent=1), encoding="utf-8")
    (OUT / f"{stem}_report.md").write_text(report(results, provenance), encoding="utf-8")
    print(f"wrote {OUT / (stem + '_report.md')}")
    for s in provenance["splits_run"]:
        r = results[s]["systems"]
        print(s, {k: (r[k]["counts"]["failed"], r[k]["labels_strict"]["recommended"]["f1"]) for k in SYSTEMS})
    return 0


if __name__ == "__main__":
    sys.exit(main())
