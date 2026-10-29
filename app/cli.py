"""Command-line entry points (same services as the API).

  python -m app.cli init-db
  python -m app.cli import-pack
  python -m app.cli analyse [--provider replay|ollama|stub] [--record] [--ids id1,id2] [--only-unrecorded]
                            [--prompt-version classify-v2|classify-v1]
  python -m app.cli draft-report [<analysis_id>]   (default: the latest analysis; creates a DRAFT only)
  python -m app.cli report-diff <base_report_id> <other_report_id> [--out file.md]
  python -m app.cli write-output <analysis_id> [--out outputs/analysis_output.json] [--active-minutes N]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from app.config import ROOT, Identity, load_settings
from app.db import connect, init_db
from app.services import analysis, ingestion, review, scoring
from app.services.analyzer import PROMPT_VERSION, PROMPTS
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
    a.add_argument("--prompt-version", default=PROMPT_VERSION, choices=sorted(PROMPTS),
                   help="classification prompt (default: production classify-v2; classify-v1 reproduces the approved run)")
    a.add_argument("--only-unrecorded", action="store_true",
                   help="resume: analyse only responses without a replay recording (use with --record)")
    d = sub.add_parser("draft-report", help="create a draft report as the analyst; never submits or approves")
    d.add_argument("analysis_id", nargs="?", help="default: the most recent analysis")
    rd = sub.add_parser("report-diff", help="compare two reports (latest approved version, else latest)")
    rd.add_argument("base_report_id")
    rd.add_argument("other_report_id")
    rd.add_argument("--out", help="also write the markdown to this file")
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
        provider = analysis.build_provider(args.provider or s.provider, s, version=args.prompt_version)
        record_dir = analysis.replay_dir(s, args.prompt_version) if args.record else None
        ids = args.ids.split(",") if args.ids else None
        if args.only_unrecorded:
            rec_dir = analysis.replay_dir(s, args.prompt_version)
            all_ids = ids or [r["response_id"] for r in conn.execute("SELECT response_id FROM responses")]
            ids = [i for i in all_ids if not analysis.has_valid_recording(conn, rec_dir, i, args.prompt_version)]
            print(f"resume: {len(all_ids) - len(ids)} validly recorded, {len(ids)} to analyse", file=sys.stderr)
            if not ids:
                return 0

        def progress(i, n, rid):
            print(f"[{i}/{n}] {rid}", file=sys.stderr, flush=True)

        aid = analysis.run_analysis(conn, s, provider, actor=actor, response_ids=ids, record_dir=record_dir,
                                    progress=progress, version=args.prompt_version)
        run = analysis.get_run(conn, aid)
        print(json.dumps({k: run[k] for k in ("analysis_id", "status", "execution_mode", "model", "counts")}))
    elif args.cmd == "draft-report":
        row = conn.execute("SELECT analysis_id FROM analysis_runs ORDER BY started_at DESC, rowid DESC LIMIT 1").fetchone()
        aid = args.analysis_id or (row["analysis_id"] if row else None)
        if aid is None:
            print("no analysis to draft a report from; run analyse first", file=sys.stderr)
            return 1
        rep = review.create_report(conn, aid, _analyst(s))
        print(json.dumps({k: rep[k] for k in ("report_id", "analysis_id", "latest_status")}))
    elif args.cmd == "report-diff":
        md = review.compare_reports(conn, args.base_report_id, args.other_report_id)["markdown"]
        if args.out:
            Path(args.out).write_text(md, encoding="utf-8")
        print(md)
    elif args.cmd == "write-output":
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        run = analysis.get_run(conn, args.analysis_id)
        rows = analysis.result_rows(conn, args.analysis_id)
        draft = build_draft(conn, args.analysis_id)
        doc = {"analysis": run, "summary": scoring.aggregate(rows),
               "diagnostics": draft["diagnostics"], "remedies": draft["remedies"],
               "active_time": {"minutes": args.active_minutes, "source": "TIME_LOG.md",
                               "note": ("Candidate active time as self-reported in TIME_LOG.md (estimates marked there). "
                                        "AI-assisted session time and unattended model-run time are listed separately.")},
               "note": "Auto-generated draft diagnostics/remedies; the reviewed version is the approved report export.",
               "results": rows}
        out.write_text(json.dumps(doc, indent=1, ensure_ascii=False), encoding="utf-8")
        print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
