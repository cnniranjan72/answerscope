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


def test_backup_db_makes_a_checked_copy_and_never_overwrites(settings, monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(cli, "load_settings", lambda: settings)
    cli.main(["import-pack"])
    cli.main(["analyse", "--provider", "stub"])
    cli.main(["draft-report"])
    capsys.readouterr()
    out = tmp_path / "b.db"
    assert cli.main(["backup-db", "--out", str(out)]) == 0
    res = json.loads(capsys.readouterr().out)
    assert res["integrity_check"] == "ok" and res["rows"]["reports"] == 1 and res["rows"]["analysis_runs"] == 1
    assert connect(out).execute("SELECT COUNT(*) FROM report_versions").fetchone()[0] == 1
    assert cli.main(["backup-db", "--out", str(out)]) == 1  # existing file is never overwritten


def test_write_output_uses_the_approved_report_when_asked(settings, monkeypatch, capsys, tmp_path, client):
    from tests.conftest import A
    from tests.test_review import decide, submit
    monkeypatch.setattr(cli, "load_settings", lambda: settings)
    client.post("/datasets/pack", headers=A)
    aid = client.post("/analyses", headers=A, json={"provider": "stub"}).json()["analysis_id"]
    rid = client.post("/reports", headers=A, json={"analysis_id": aid}).json()["report_id"]
    out = tmp_path / "o.json"
    assert cli.main(["write-output", aid, "--out", str(out), "--report", rid]) == 1  # not approved yet
    c = client.get(f"/reports/{rid}", headers=A).json()["latest"]["content"]
    c["diagnostics"][0]["title"] = "Edited by the analyst before approval"
    client.patch(f"/reports/{rid}", headers=A, json={"base_version": 1, "diagnostics": c["diagnostics"]})
    submit(client, rid, 1)
    decide(client, rid, 1)
    assert cli.main(["write-output", aid, "--out", str(out), "--report", rid, "--active-minutes", "5"]) == 0
    doc = json.loads(out.read_text(encoding="utf-8"))
    assert doc["diagnostics"][0]["title"] == "Edited by the analyst before approval"
    assert "approved report" in doc["note"] and doc["active_time"]["minutes"] == 5
