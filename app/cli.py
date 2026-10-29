"""Command-line entry points (same services as the API).

  python -m app.cli init-db
  python -m app.cli import-pack
  python -m app.cli analyse [--provider replay|ollama|stub] [--record] [--ids id1,id2] [--only-unrecorded]
  python -m app.cli write-output <analysis_id> [--out outputs/analysis_output.json] [--active-minutes N]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from app.config import ROOT, Identity, load_settings
from app.db import connect, init_db
from app.services import analysis, ingestion, scoring
from app.services.analyzer import PROMPT_VERSION
from app.services.reporting import build_draft

CLI_ACTOR = "cli-analyst"


def _analyst(settings) -> Identity:
    return next(i for i in settings.tokens.values() if i.role == "analyst")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m app.cli")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init-db")
    sub.add_parser("import-pack")
    a = sub.add_parser("analyse")
    a.add_argument("--provider", choices=["replay", "ollama", "stub"])
    a.add_argument("--record", action="store_true", help="with --provider ollama: write replay recordings")
    a.add_argument("--ids", help="comma-separated response IDs (default: all)")
    a.add_argument("--only-unrecorded", action="store_true",
                   help="resume: analyse only responses without a replay recording (use with --record)")
    w = sub.add_parser("write-output")
    w.add_argument("analysis_id")
    w.add_argument("--out", default=str(ROOT / "outputs" / "analysis_output.json"))
    w.add_argument("--active-minutes", type=int, help="actual active work time to record (brief requirement)")
    args = ap.parse_args(argv)

    s = load_settings()
    init_db(s.db_path)
    conn = connect(s.db_path)
    actor = _analyst(s).name
    if args.cmd == "init-db":
        print(f"database ready: {s.db_path}")
    elif args.cmd == "import-pack":
        res = ingestion.import_records(conn, ingestion.load_pack(s.pack_dir), actor=actor, source="configured_pack")
        print(json.dumps({k: res[k] for k in ("dataset_id", "counts", "rejections")}, indent=1))
    elif args.cmd == "analyse":
        provider = analysis.build_provider(args.provider or s.provider, s)
        record_dir = s.replay_dir / PROMPT_VERSION.replace("-", "_") if args.record else None
        ids = args.ids.split(",") if args.ids else None
        if args.only_unrecorded:
            rec_dir = s.replay_dir / PROMPT_VERSION.replace("-", "_")
            all_ids = ids or [r["response_id"] for r in conn.execute("SELECT response_id FROM responses")]
            ids = [i for i in all_ids if not (rec_dir / f"{i}.json").exists()]
            print(f"resume: {len(all_ids) - len(ids)} already recorded, {len(ids)} to analyse", file=sys.stderr)
            if not ids:
                return 0

        def progress(i, n, rid):
            print(f"[{i}/{n}] {rid}", file=sys.stderr, flush=True)

        aid = analysis.run_analysis(conn, s, provider, actor=actor, response_ids=ids, record_dir=record_dir,
                                    progress=progress)
        run = analysis.get_run(conn, aid)
        print(json.dumps({k: run[k] for k in ("analysis_id", "status", "execution_mode", "model", "counts")}))
    elif args.cmd == "write-output":
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        run = analysis.get_run(conn, args.analysis_id)
        rows = analysis.result_rows(conn, args.analysis_id)
        draft = build_draft(conn, args.analysis_id)
        doc = {"analysis": run, "summary": scoring.aggregate(rows),
               "diagnostics": draft["diagnostics"], "remedies": draft["remedies"],
               "active_time": {"minutes": args.active_minutes, "source": "TIME_LOG.md",
                               "note": "Active work only; unattended model-run time is excluded."},
               "note": "Auto-generated draft diagnostics/remedies; the reviewed version is the approved report export.",
               "results": rows}
        out.write_text(json.dumps(doc, indent=1, ensure_ascii=False), encoding="utf-8")
        print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
