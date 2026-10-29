"""Offline export verification: a recipient can check an export file without the database."""
from __future__ import annotations

import copy
import json

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
