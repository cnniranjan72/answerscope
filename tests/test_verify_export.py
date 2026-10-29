"""Offline export verification: a recipient can check an export file without the database."""
from __future__ import annotations

import copy
import json
from pathlib import Path

from app.verify_export import main, verify
from tests.conftest import A, MINI_PACK
from tests.test_review import decide, submit


def exported(client, report):
    rid = report["report_id"]
    submit(client, rid, 1)
    decide(client, rid, 1)
    return client.get(f"/reports/{rid}/export", headers=A).json()


def answers():
    out = {}
    for f in MINI_PACK.rglob("responses.jsonl"):
        for line in f.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                out[r["response_id"]] = r["answer_text"]
    return out


def test_untouched_export_verifies_including_every_quote_location(client, report):
    doc = exported(client, report)
    checks = verify(doc, answers())
    assert all(ok for _, ok, _ in checks), checks
    assert len(checks) == 6


def test_edited_content_fails_the_hash_check(client, report):
    doc = copy.deepcopy(exported(client, report))
    doc["content"]["executive_summary"] += " (edited after approval)"
    assert dict((n, ok) for n, ok, _ in verify(doc))["content hash"] is False


def test_moved_quote_location_fails_and_cli_exits_nonzero(client, report, tmp_path, capsys):
    doc = copy.deepcopy(exported(client, report))
    doc["content"]["diagnostics"][0]["evidence"][0]["location"]["start"] += 1
    f = tmp_path / "export.json"
    f.write_text(json.dumps(doc), encoding="utf-8")
    pack = tmp_path / "responses.jsonl"
    pack.write_text("".join(json.dumps({"response_id": k, "answer_text": v}) + "\n" for k, v in answers().items()),
                    encoding="utf-8")
    assert main([str(f), "--answers", str(pack)]) == 1
    out = capsys.readouterr().out
    assert "FAIL  quotes found" in out and "NOT verified" in out
    assert "PASS  content hash" in out  # location is export-only metadata, outside the hash


def test_render_produces_a_readable_report_only_from_a_verified_export(client, report, tmp_path, capsys):
    from app.render_export import main as render_main, render
    doc = exported(client, report)
    md = render(doc)
    assert md.startswith("# ") and doc["content_sha256"] in md
    for heading in ("## Summary", "## Scorecard", "## Diagnostics", "## Remedies", "## Limitations", "## Method"):
        assert heading in md
    assert all(d["title"] in md for d in doc["content"]["diagnostics"])
    good, bad, out = tmp_path / "good.json", tmp_path / "bad.json", tmp_path / "report.md"
    good.write_text(json.dumps(doc), encoding="utf-8")
    assert render_main([str(good), "--out", str(out)]) == 0 and out.read_text(encoding="utf-8") == md
    tampered = copy.deepcopy(doc)
    tampered["content"]["diagnostics"][0]["title"] = "Something the reviewer never approved"
    bad.write_text(json.dumps(tampered), encoding="utf-8")
    out.unlink()
    assert render_main([str(bad), "--out", str(out)]) == 1 and not out.exists()
    assert "REFUSED" in capsys.readouterr().err


def test_markdown_export_endpoint_renders_only_approved_versions(client, report):
    rid = report["report_id"]
    assert client.get(f"/reports/{rid}/export.md", headers=A).status_code == 409  # draft: refused like JSON export
    assert client.get(f"/reports/{rid}/export.md").status_code == 401
    submit(client, rid, 1)
    decide(client, rid, 1)
    r = client.get(f"/reports/{rid}/export.md", headers=A)
    assert r.status_code == 200 and r.headers["content-type"].startswith("text/markdown")
    assert "attachment" in r.headers["content-disposition"] and "## Diagnostics" in r.text
    assert client.get(f"/reports/{rid}/export", headers=A).json()["content_sha256"] in r.text


def test_regression_f6_reserialised_numbers_fail_and_console_saves_raw_bytes(client, report):
    """F6: the console re-serialised the export with JSON.stringify, which writes 1.0 as 1;
    the canonical content changed and the hash failed. The console now saves the server's bytes."""
    doc = exported(client, report)

    def js_like(x):  # what JSON.stringify does to whole-number floats
        if isinstance(x, float) and x.is_integer():
            return int(x)
        if isinstance(x, dict):
            return {k: js_like(v) for k, v in x.items()}
        if isinstance(x, list):
            return [js_like(v) for v in x]
        return x

    reserialised = js_like(copy.deepcopy(doc))
    assert json.dumps(reserialised, sort_keys=True) != json.dumps(doc, sort_keys=True)  # whole-number floats, e.g. 1.0
    checks = {n: (ok, d) for n, ok, d in verify(reserialised)}
    assert checks["content hash"][0] is False and "re-export" in checks["content hash"][1]
    console = (Path(__file__).resolve().parents[1] / "app" / "static" / "index.html").read_text(encoding="utf-8")
    assert "new Blob([text]" in console and "JSON.stringify(r, null" not in console
