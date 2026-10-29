"""Required: incorrect reviewer role; rejection blocks export; edit-after-approval needs a
new review. Plus the end-to-end workflow, immutability and evidence checks."""
import sqlite3

import pytest

from app.services.text import answer_body, locate
from tests.conftest import A, R


def latest(client, rid):
    return client.get(f"/reports/{rid}", headers=A).json()


def submit(client, rid, v):
    return client.post(f"/reports/{rid}/submit", headers=A, json={"version": v})


def decide(client, rid, v, decision="approve", headers=R, sha=None, comment="Checked evidence against sources."):
    sha = sha or client.get(f"/reports/{rid}/versions/{v}", headers=A).json()["content_sha256"]
    return client.post(f"/reports/{rid}/decision", headers=headers,
                       json={"version": v, "decision": decision, "comment": comment, "content_sha256": sha})


def test_end_to_end_import_analyse_edit_submit_approve_export(client, report):
    rid = report["report_id"]
    assert report["latest_status"] == "draft" and report["evidence_problems"] == []
    content = report["latest"]["content"]
    assert len(content["diagnostics"]) == 3 and len(content["remedies"]) == 3
    assert content["provenance"]["execution_mode"] == "stub"

    r = client.patch(f"/reports/{rid}", headers=A, json={"base_version": 1, "executive_summary": "Edited by analyst."})
    assert r.status_code == 200 and r.json()["version"] == 1 and not r.json()["new_version_created"]
    assert submit(client, rid, 1).status_code == 200
    r = decide(client, rid, 1)
    assert r.status_code == 200 and r.json()["latest_status"] == "approved"
    dec = r.json()["decisions"][0]
    assert (dec["actor"], dec["actor_role"], dec["version"], dec["decision"]) == ("rita-reviewer", "reviewer", 1, "approved")
    assert dec["comment"] and dec["decided_at"] and len(dec["content_sha256"]) == 64

    ex = client.get(f"/reports/{rid}/export", headers=A)
    assert ex.status_code == 200
    body = ex.json()
    assert body["version"] == 1 and body["is_latest_version"] and body["approval"]["reviewer"] == "rita-reviewer"
    assert body["content"]["executive_summary"] == "Edited by analyst."
    ev = body["content"]["diagnostics"][0]["evidence"][0]
    assert ev["location"]["start"] < ev["location"]["end"] and ev["engine"] in {"aimode", "chatgpt", "gemini"}


def test_wrong_role_denied(client, report):
    rid = report["report_id"]
    submit(client, rid, 1)
    r = decide(client, rid, 1, headers=A)  # analyst tries to approve
    assert r.status_code == 403 and r.json()["error"]["code"] == "forbidden"
    assert client.patch(f"/reports/{rid}", headers=R, json={"base_version": 1, "title": "Reviewer edit"}).status_code == 403
    assert client.post("/analyses", headers=R, json={}).status_code == 403
    assert latest(client, rid)["latest_status"] == "submitted"  # nothing changed


def test_caller_supplied_identity_is_not_authorisation(client, report):
    rid = report["report_id"]
    submit(client, rid, 1)
    sha = client.get(f"/reports/{rid}/versions/1", headers=A).json()["content_sha256"]
    r = client.post(f"/reports/{rid}/decision", headers=A,
                    json={"version": 1, "decision": "approve", "comment": "ok", "content_sha256": sha,
                          "role": "reviewer", "actor": "rita-reviewer"})
    assert r.status_code in (403, 422)  # forged fields never grant authority
    r = client.post(f"/reports/{rid}/decision", headers={**A, "X-Role": "reviewer"},
                    json={"version": 1, "decision": "approve", "comment": "ok", "content_sha256": sha})
    assert r.status_code == 403


@pytest.mark.parametrize("headers,code", [({}, 401), ({"Authorization": "Bearer not-a-real-token-xxxxx"}, 401)])
def test_unauthenticated(client, report, headers, code):
    r = client.get(f"/reports/{report['report_id']}/export", headers=headers)
    assert r.status_code == code and r.json()["error"]["code"] == "unauthenticated"
    assert "test-analyst-token" not in r.text


def test_rejection_blocks_export(client, report):
    rid = report["report_id"]
    submit(client, rid, 1)
    r = decide(client, rid, 1, decision="reject", comment="D2 evidence is too thin.")
    assert r.status_code == 200 and r.json()["latest_status"] == "rejected"
    for url in (f"/reports/{rid}/export", f"/reports/{rid}/export?version=1"):
        ex = client.get(url, headers=A)
        assert ex.status_code == 409 and ex.json()["error"]["code"] == "not_approved"
    assert decide(client, rid, 1).status_code == 409  # cannot flip a decided version
    assert submit(client, rid, 1).status_code == 409  # cannot resubmit rejected content
    r = client.patch(f"/reports/{rid}", headers=A, json={"base_version": 1, "analyst_notes": "Addressed review."})
    assert r.json()["version"] == 2 and r.json()["status"] == "draft"


def test_edit_after_approval_requires_new_review(client, report):
    rid = report["report_id"]
    submit(client, rid, 1)
    decide(client, rid, 1)
    r = client.patch(f"/reports/{rid}", headers=A, json={"base_version": 1, "title": "Changed after approval"})
    assert r.status_code == 200 and r.json()["new_version_created"] and r.json()["version"] == 2
    assert client.get(f"/reports/{rid}/versions/1", headers=A).json()["status"] == "approved"

    ex = client.get(f"/reports/{rid}/export", headers=A)  # latest is an unreviewed draft
    assert ex.status_code == 409 and ex.json()["error"]["details"]["latest_approved_version"] == 1
    old = client.get(f"/reports/{rid}/export?version=1", headers=A)  # old approval: only its own content
    assert old.status_code == 200 and old.json()["superseded_by_version"] == 2
    assert old.json()["content"]["title"] != "Changed after approval"
    assert decide(client, rid, 2).status_code == 409  # draft cannot be approved without submission

    assert submit(client, rid, 2).status_code == 200
    assert decide(client, rid, 2).status_code == 200
    ex = client.get(f"/reports/{rid}/export", headers=A)
    assert ex.status_code == 200 and ex.json()["version"] == 2 and ex.json()["content"]["title"] == "Changed after approval"


def test_editing_submitted_version_supersedes_it(client, report):
    rid = report["report_id"]
    submit(client, rid, 1)
    client.patch(f"/reports/{rid}", headers=A, json={"base_version": 1, "analyst_notes": "late fix"})
    r = decide(client, rid, 1)
    assert r.status_code == 409 and r.json()["error"]["code"] == "stale_version"


def test_stale_base_version_rejected(client, report):
    rid = report["report_id"]
    submit(client, rid, 1)
    client.patch(f"/reports/{rid}", headers=A, json={"base_version": 1, "analyst_notes": "v2"})
    r = client.patch(f"/reports/{rid}", headers=A, json={"base_version": 1, "analyst_notes": "lost update"})
    assert r.status_code == 409 and r.json()["error"]["code"] == "stale_version"


def test_decision_hash_must_match_reviewed_content(client, report):
    rid = report["report_id"]
    submit(client, rid, 1)
    r = decide(client, rid, 1, sha="0" * 64)
    assert r.status_code == 409 and r.json()["error"]["code"] == "content_mismatch"


def test_decision_requires_comment(client, report):
    rid = report["report_id"]
    submit(client, rid, 1)
    assert decide(client, rid, 1, comment="  ").status_code == 422


def test_double_submit_rejected(client, report):
    rid = report["report_id"]
    assert submit(client, rid, 1).status_code == 200
    assert submit(client, rid, 1).status_code == 409


def test_no_silent_approval_without_reviewer(client, report):
    """review_no_response fixture: nothing approves on its own; the version waits."""
    rid = report["report_id"]
    submit(client, rid, 1)
    assert client.get(f"/reports/{rid}/export", headers=A).status_code == 409
    assert latest(client, rid)["latest_status"] == "submitted"


def test_fabricated_evidence_blocks_submission(client, report):
    rid = report["report_id"]
    diags = report["latest"]["content"]["diagnostics"]
    diags[0]["evidence"][0]["quote"] = "Kasparro is the clear market leader trusted by every Fortune 500 firm."
    r = client.patch(f"/reports/{rid}", headers=A, json={"base_version": 1, "diagnostics": diags})
    assert r.status_code == 200 and any("quote not found" in p for p in r.json()["evidence_problems"])
    r = submit(client, rid, 1)
    assert r.status_code == 422 and r.json()["error"]["code"] == "evidence_check_failed"


def test_remedy_must_follow_from_its_diagnostic(client, report):
    rid = report["report_id"]
    rem = report["latest"]["content"]["remedies"]
    rem[0]["evidence"] = report["latest"]["content"]["diagnostics"][1]["evidence"][:1]
    if rem[0]["evidence"] == report["latest"]["content"]["diagnostics"][0]["evidence"][:1]:
        pytest.skip("diagnostics share evidence")
    client.patch(f"/reports/{rid}", headers=A, json={"base_version": 1, "remedies": rem})
    r = submit(client, rid, 1)
    assert r.status_code == 422 and any("not drawn from its diagnostic" in p for p in r.json()["error"]["details"]["problems"])


def test_database_refuses_to_alter_frozen_version(client, report, conn):
    rid = report["report_id"]
    submit(client, rid, 1)
    with pytest.raises(sqlite3.IntegrityError, match="frozen"):
        conn.execute("UPDATE report_versions SET content_json = '{}' WHERE report_id = ? AND version = 1", (rid,))
    with pytest.raises(sqlite3.IntegrityError, match="invalid report status transition"):
        conn.execute("UPDATE report_versions SET status = 'draft' WHERE report_id = ?", (rid,))
    with pytest.raises(sqlite3.IntegrityError, match="append-only"):
        conn.execute("DELETE FROM report_versions WHERE report_id = ?", (rid,))


def test_tampered_approved_content_fails_export_integrity(client, report, conn):
    rid = report["report_id"]
    submit(client, rid, 1)
    decide(client, rid, 1)
    conn.execute("DROP TRIGGER trg_frozen_content")  # simulate out-of-band tampering
    conn.execute("UPDATE report_versions SET content_json = '{\"title\":\"forged\"}' WHERE report_id = ?", (rid,))
    r = client.get(f"/reports/{rid}/export", headers=A)
    assert r.status_code == 409 and r.json()["error"]["code"] == "integrity_error"


def test_competitor_counting_ignores_spelling_variants():
    from app.services.reporting import comp_key
    assert comp_key("Otterly.ai") == comp_key("Otterly AI") == comp_key("otterly-ai")
    assert comp_key("OtterlyAI") == comp_key("Otterly") and comp_key("Peec AI") == comp_key("Peec")  # draft v2 review
    from app.services.reporting import REPORT_GENERATOR_VERSION
    assert REPORT_GENERATOR_VERSION == "report-v2"  # counting changed: version bumped (CLAUDE.md)
    assert comp_key("HubSpot AEO") != comp_key("HubSpot")


def test_remedy_problem_text_has_single_full_stop(client, report):
    content = report["latest"]["content"]
    for r in content["remedies"]:
        assert ".." not in r["problem"], r["problem"]


def test_analyst_can_remove_weak_evidence_and_still_submit(client, report):
    """The console lets the analyst drop a weak quote from a diagnostic and its remedy."""
    rid, c = report["report_id"], report["latest"]["content"]
    d0 = c["diagnostics"][0]
    if len(d0["evidence"]) < 2:
        pytest.skip("needs two evidence items")
    drop = d0["evidence"][0]
    d0["evidence"] = d0["evidence"][1:]
    r0 = next(r for r in c["remedies"] if r["diagnostic_id"] == d0["id"])
    r0["evidence"] = [e for e in r0["evidence"] if e != drop] or d0["evidence"][:1]
    r = client.patch(f"/reports/{rid}", headers=A, json={"base_version": 1, "diagnostics": c["diagnostics"],
                                                          "remedies": c["remedies"]})
    assert r.status_code == 200, r.text
    assert drop not in latest(client, rid)["latest"]["content"]["diagnostics"][0]["evidence"]
    assert submit(client, rid, 1).status_code == 200


def test_export_hash_is_verifiable_from_the_file(client, report):
    from app.services.reporting import canonical, sha256
    from app.services.review import EXPORT_EVIDENCE_FIELDS
    rid = report["report_id"]
    submit(client, rid, 1)
    decide(client, rid, 1)
    ex = client.get(f"/reports/{rid}/export", headers=A).json()
    content = ex["content"]
    for section in ("diagnostics", "remedies"):
        for item in content[section]:
            for e in item["evidence"]:
                for k in EXPORT_EVIDENCE_FIELDS:
                    e.pop(k)
    assert sha256(canonical(content)) == ex["content_sha256"]


def test_weak_evidence_is_flagged_but_does_not_block(client, report, conn):
    """evidence-v2: a verbatim but very short quote is shown as a warning; submission still works."""
    rid, c = report["report_id"], report["latest"]["content"]
    d0 = c["diagnostics"][0]
    e = d0["evidence"][0]
    body = answer_body(conn.execute("SELECT answer_text FROM responses WHERE response_id = ?",
                                    (e["response_id"],)).fetchone()["answer_text"])
    e["quote"] = body[locate(e["quote"], body)[0]:][:8]  # real, verbatim, but too short to be strong
    for r in c["remedies"]:
        if r["diagnostic_id"] == d0["id"]:
            r["evidence"] = [e]
    client.patch(f"/reports/{rid}", headers=A, json={"base_version": 1, "diagnostics": c["diagnostics"],
                                                      "remedies": c["remedies"]})
    view = latest(client, rid)
    assert "very short quote" in view["evidence_warnings"][f"{d0['id']}#1"]
    assert not view["evidence_problems"]
    assert submit(client, rid, 1).status_code == 200


def test_review_deadline_flags_overdue_and_never_auto_approves(client, report, conn):
    """Fixture scenario review_no_response: a short simulated deadline must not approve."""
    rid = report["report_id"]
    assert submit(client, rid, 1).status_code == 200
    v = latest(client, rid)["latest"]
    assert v["review_due_at"] and v["review_overdue"] is False
    conn.execute("UPDATE report_versions SET review_due_at = '2000-01-01T00:00:00+00:00' WHERE report_id = ?", (rid,))
    conn.commit()
    view = latest(client, rid)
    assert view["latest"]["review_overdue"] is True and view["latest_status"] == "submitted"
    assert client.get(f"/reports/{rid}/export", headers=A).status_code == 409  # still not exportable
    assert decide(client, rid, 1).status_code == 200  # a late human decision is still valid (hash-checked)
    assert latest(client, rid)["latest"]["review_overdue"] is False


def test_migration_adds_review_deadline_to_an_old_database(tmp_path):
    from app.db import connect, init_db
    db = tmp_path / "old.db"
    c = sqlite3.connect(db)
    c.execute("CREATE TABLE report_versions (report_id TEXT, version INTEGER, status TEXT, content_json TEXT, "
              "content_sha256 TEXT, parent_version INTEGER, created_by TEXT, created_at TEXT, updated_at TEXT, "
              "submitted_by TEXT, submitted_at TEXT, PRIMARY KEY (report_id, version))")
    c.commit(); c.close()
    init_db(db); init_db(db)  # idempotent
    assert "review_due_at" in {r[1] for r in connect(db).execute("PRAGMA table_info(report_versions)")}
