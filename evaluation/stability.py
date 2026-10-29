"""Repeated-run stability: does a fresh live call reproduce the recorded labels?

  python -m evaluation.stability --version classify-v1 --splits final_seen,holdout2 --runs 1

For each case, calls the local model again (same prompt, temperature 0, seed 7, no
recording) and compares every label with the recorded (replay) result. Reports per-label
agreement, flips by case, and failures. This measures run-to-run reproducibility of
the live model at the fixed settings; it does not measure variance at temperature > 0.
Writes evaluation/results/stability_<version>.md and .json. Never overwrites recordings.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from app.config import load_settings
from app.db import utcnow
from evaluation.compare import SPLIT_ORDER, load_cases, run, wilson
from evaluation.run_eval import LABELS, load_pack_index
from app.services.analysis import build_provider

OUT = Path(__file__).resolve().parents[1] / "evaluation" / "results"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m evaluation.stability")
    ap.add_argument("--version", default="classify-v1", choices=["classify-v1", "classify-v2"])
    ap.add_argument("--splits", default="final_seen,holdout2")
    ap.add_argument("--runs", type=int, default=1)
    args = ap.parse_args(argv)
    splits = load_cases()
    names = args.splits.split(",")
    if not set(names) <= set(SPLIT_ORDER):
        ap.error("unknown split")
    cases = [c for s in names for c in splits[s]]
    settings = load_settings()
    pack = load_pack_index(settings.pack_dir)
    recorded = run(args.version, cases, pack, settings, build_provider("replay", settings, version=args.version))
    live = build_provider("ollama", settings, version=args.version)
    runs = [run(args.version, cases, pack, settings, live) for _ in range(args.runs)]

    agree, n, flips, fails = Counter(), Counter(), [], Counter()
    for i, rr in enumerate(runs, start=1):
        for c in cases:
            a, b = recorded[c["case_id"]], rr[c["case_id"]]
            if a["status"] != "succeeded" or b["status"] != "succeeded":
                fails[f"run{i}:{a['status']}->{b['status']}"] += 1
                continue
            for lab in LABELS:
                n[lab] += 1
                same = a["pred"]["labels"][lab] == b["pred"]["labels"][lab]
                agree[lab] += same
                if not same:
                    flips.append({"run": i, "case": c["case_id"], "label": lab,
                                  "recorded": a["pred"]["labels"][lab], "live": b["pred"]["labels"][lab]})
    res = {"generated_at": utcnow(), "version": args.version, "splits": names, "cases": len(cases), "runs": args.runs,
           "settings": {"temperature": 0, "seed": 7, "model": live.model},
           "agreement": {lab: {"agree": agree[lab], "n": n[lab], "rate": round(agree[lab] / n[lab], 3) if n[lab] else None,
                               "ci95": wilson(agree[lab], n[lab])} for lab in LABELS},
           "flips": flips, "status_changes": dict(fails)}
    OUT.mkdir(parents=True, exist_ok=True)
    stem = f"stability_{args.version.replace('-', '_')}"
    (OUT / f"{stem}.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    lines = [f"# Repeated-run stability: {args.version}", "",
             f"Generated {res['generated_at']} | {len(cases)} cases ({', '.join(names)}) | {args.runs} live re-run(s) "
             f"vs the recorded run | temperature 0, seed 7, `{live.model}`", "",
             "| Label | Agree / compared | Rate | Wilson 95% |", "|---|---|---|---|"]
    for lab, v in res["agreement"].items():
        lines.append(f"| {lab} | {v['agree']}/{v['n']} | {v['rate']} | {v['ci95']} |")
    lines += ["", f"Status changes (recorded -> live): {res['status_changes'] or 'none'}", "",
              "Label flips: " + (", ".join(f"{f['case']} {f['label']} {f['recorded']}->{f['live']}" for f in flips) or "none"), ""]
    (OUT / f"{stem}.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
