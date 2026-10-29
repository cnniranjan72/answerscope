"""CLI draft-report: used by the demo image to seed a reviewable draft."""
from __future__ import annotations

import json

from app import cli
from app.db import connect


def test_draft_report_creates_a_draft_from_the_latest_analysis_and_never_submits(settings, monkeypatch, capsys):
    monkeypatch.setattr(cli, "load_settings", lambda: settings)
    assert cli.main(["draft-report"]) == 1  # nothing analysed yet
    cli.main(["import-pack"])
    cli.main(["analyse", "--provider", "stub"])
    capsys.readouterr()
    assert cli.main(["draft-report"]) == 0
    out = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert out["latest_status"] == "draft"
    conn = connect(settings.db_path)
    statuses = [r["status"] for r in conn.execute("SELECT status FROM report_versions")]
    assert statuses == ["draft"]
    assert conn.execute("SELECT COUNT(*) FROM review_decisions").fetchone()[0] == 0
