"""Report versions, review decisions and export authorisation.

State machine per version:  draft --submit--> submitted --decision--> approved | rejected
  * Only the latest version can be edited, submitted or decided.
  * Editing a draft changes it in place; editing a submitted/approved/rejected version
    creates a new draft (version + 1). The frozen version stays unchanged (enforced
    here and by SQLite triggers).
  * A decision names the version and the SHA-256 of the content the reviewer read; it
    is refused if that version is not 'submitted', is no longer the latest, or the
    hash differs.
  * Export returns only approved content. The default target is the latest version; an
    older approved version is exportable only when requested explicitly by number, and
    it is labelled as superseded.
Every state transition runs inside BEGIN IMMEDIATE, so check and write are atomic.
"""
from __future__ import annotations

import json
import sqlite3
import uuid

from app.config import Identity
from app.db import transaction, utcnow
from app.errors import Conflict, Forbidden, NotFound, Unprocessable
from app.schemas import DecisionRequest, ReportPatch
from app.services.analysis import get_run
from app.services.reporting import build_draft, canonical, enrich_evidence, sha256, verify_content, evidence_warnings

EDITABLE_FIELDS = ("title", "executive_summary", "diagnostics", "remedies", "analyst_notes")


def _latest(conn: sqlite3.Connection, report_id: str) -> sqlite3.Row:
    row = conn.execute("SELECT * FROM report_versions WHERE report_id = ? ORDER BY version DESC LIMIT 1",
                       (report_id,)).fetchone()
    if row is None:
        raise NotFound(f"report {report_id} not found")
    return row


def _version(conn: sqlite3.Connection, report_id: str, version: int) -> sqlite3.Row:
    row = conn.execute("SELECT * FROM report_versions WHERE report_id = ? AND version = ?",
                       (report_id, version)).fetchone()
    if row is None:
        raise NotFound(f"report {report_id} version {version} not found")
    return row


def _version_view(row: sqlite3.Row, include_content: bool = True) -> dict:
    d = {k: row[k] for k in ("report_id", "version", "status", "content_sha256", "parent_version",
                             "created_by", "created_at", "updated_at", "submitted_by", "submitted_at")}
    if include_content:
        d["content"] = json.loads(row["content_json"])
    return d


def create_report(conn: sqlite3.Connection, analysis_id: str, actor: Identity) -> dict:
    get_run(conn, analysis_id)  # 404 if missing
    content = build_draft(conn, analysis_id)
    text = canonical(content)
    report_id = str(uuid.uuid4())
    now = utcnow()
    with transaction(conn):
        conn.execute("INSERT INTO reports VALUES (?, ?, ?, ?)", (report_id, analysis_id, actor.name, now))
        conn.execute("INSERT INTO report_versions (report_id, version, status, content_json, content_sha256, "
                     "parent_version, created_by, created_at, updated_at) VALUES (?, 1, 'draft', ?, ?, NULL, ?, ?, ?)",
                     (report_id, text, sha256(text), actor.name, now, now))
    return get_report(conn, report_id)


def get_report(conn: sqlite3.Connection, report_id: str) -> dict:
    rep = conn.execute("SELECT * FROM reports WHERE report_id = ?", (report_id,)).fetchone()
    if rep is None:
        raise NotFound(f"report {report_id} not found")
    versions = conn.execute("SELECT * FROM report_versions WHERE report_id = ? ORDER BY version",
                            (report_id,)).fetchall()
    decisions = conn.execute("SELECT * FROM review_decisions WHERE report_id = ? ORDER BY decision_id",
                             (report_id,)).fetchall()
    latest = versions[-1]
    approved = [v["version"] for v in versions if v["status"] == "approved"]
    return {
        "report_id": report_id, "analysis_id": rep["analysis_id"], "created_by": rep["created_by"],
        "created_at": rep["created_at"],
        "latest_version": latest["version"], "latest_status": latest["status"],
        "latest_approved_version": approved[-1] if approved else None,
        "exportable": latest["status"] == "approved",
        "versions": [_version_view(v, include_content=False) for v in versions],
        "decisions": [dict(d) for d in decisions],
        "latest": _version_view(latest),
        "evidence_problems": verify_content(conn, json.loads(latest["content_json"]), for_submit=True),
        "evidence_warnings": evidence_warnings(conn, json.loads(latest["content_json"])),
    }


def get_version(conn: sqlite3.Connection, report_id: str, version: int) -> dict:
    return _version_view(_version(conn, report_id, version))


def patch_report(conn: sqlite3.Connection, report_id: str, patch: ReportPatch, actor: Identity) -> dict:
    changes = patch.model_dump(exclude_unset=True, exclude={"base_version"})
    if not changes:
        raise Unprocessable("no editable fields supplied", {"editable": list(EDITABLE_FIELDS)})
    with transaction(conn):
        latest = _latest(conn, report_id)
        if patch.base_version != latest["version"]:
            raise Conflict("stale edit: base_version is not the latest version",
                           {"base_version": patch.base_version, "latest_version": latest["version"]},
                           code="stale_version")
        content = json.loads(latest["content_json"])
        content.update(changes)
        text = canonical(content)
        now = utcnow()
        if latest["status"] == "draft":
            conn.execute("UPDATE report_versions SET content_json = ?, content_sha256 = ?, updated_at = ? "
                         "WHERE report_id = ? AND version = ?",
                         (text, sha256(text), now, report_id, latest["version"]))
            version, created = latest["version"], False
        else:
            # Frozen (submitted/approved/rejected): never modified; edits start a new draft.
            version, created = latest["version"] + 1, True
            conn.execute("INSERT INTO report_versions (report_id, version, status, content_json, content_sha256, "
                         "parent_version, created_by, created_at, updated_at) VALUES (?, ?, 'draft', ?, ?, ?, ?, ?, ?)",
                         (report_id, version, text, sha256(text), latest["version"], actor.name, now, now))
    view = get_version(conn, report_id, version)
    view["new_version_created"] = created
    view["evidence_problems"] = verify_content(conn, content, for_submit=True)
    view["evidence_warnings"] = evidence_warnings(conn, content)
    return view


def submit(conn: sqlite3.Connection, report_id: str, version: int, actor: Identity) -> dict:
    with transaction(conn):
        latest = _latest(conn, report_id)
        if version != latest["version"]:
            raise Conflict("only the latest version can be submitted",
                           {"requested": version, "latest_version": latest["version"]}, code="stale_version")
        if latest["status"] != "draft":
            raise Conflict(f"version {version} is {latest['status']}; only a draft can be submitted",
                           code="invalid_transition")
        content = json.loads(latest["content_json"])
        problems = verify_content(conn, content, for_submit=True)
        if problems:
            raise Unprocessable("report failed evidence checks; fix before submitting",
                                {"problems": problems}, code="evidence_check_failed")
        conn.execute("UPDATE report_versions SET status = 'submitted', submitted_by = ?, submitted_at = ? "
                     "WHERE report_id = ? AND version = ?", (actor.name, utcnow(), report_id, version))
    return get_version(conn, report_id, version)


def decide(conn: sqlite3.Connection, report_id: str, req: DecisionRequest, actor: Identity) -> dict:
    if actor.role != "reviewer":  # defence in depth; the API dependency checks this first
        raise Forbidden("only the configured reviewer can decide")
    with transaction(conn):
        target = _version(conn, report_id, req.version)
        latest = _latest(conn, report_id)
        if target["status"] != "submitted":
            raise Conflict(f"version {req.version} is {target['status']}; only a submitted version can be decided",
                           code="invalid_transition")
        if req.version != latest["version"]:
            raise Conflict("version has been superseded by a newer draft; review the latest version",
                           {"latest_version": latest["version"]}, code="stale_version")
        if req.content_sha256 != target["content_sha256"]:
            raise Conflict("content_sha256 does not match the submitted version",
                           {"expected_for_version": target["content_sha256"]}, code="content_mismatch")
        status = "approved" if req.decision == "approve" else "rejected"
        conn.execute("INSERT INTO review_decisions (report_id, version, decision, comment, actor, actor_role, "
                     "content_sha256, decided_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                     (report_id, req.version, status, req.comment.strip(), actor.name, actor.role,
                      target["content_sha256"], utcnow()))
        conn.execute("UPDATE report_versions SET status = ? WHERE report_id = ? AND version = ?",
                     (status, report_id, req.version))
    return get_report(conn, report_id)


EXPORT_EVIDENCE_FIELDS = ("engine", "prompt_id", "question", "location")  # added by enrich_evidence


def export(conn: sqlite3.Connection, report_id: str, version: int | None) -> dict:
    latest = _latest(conn, report_id)
    target = latest if version is None else _version(conn, report_id, version)
    if target["status"] != "approved":
        approved = conn.execute("SELECT MAX(version) AS v FROM report_versions WHERE report_id = ? AND "
                                "status = 'approved'", (report_id,)).fetchone()["v"]
        raise Conflict(
            f"version {target['version']} is {target['status']}; only an approved version can be exported",
            {"requested_version": target["version"], "status": target["status"],
             "latest_version": latest["version"], "latest_approved_version": approved,
             "hint": "an older approved version can be exported only by requesting ?version=<n> explicitly"},
            code="not_approved")
    decision = conn.execute("SELECT * FROM review_decisions WHERE report_id = ? AND version = ?",
                            (report_id, target["version"])).fetchone()
    actual = sha256(target["content_json"])
    if decision is None or actual != target["content_sha256"] or actual != decision["content_sha256"]:
        raise Conflict("integrity check failed: content does not match the approved hash", code="integrity_error")
    content = json.loads(target["content_json"])
    return {
        "export_format": "answerscope-report-export-v1",
        "report_id": report_id,
        "version": target["version"],
        "content_sha256": actual,
        "content_sha256_covers": ("the approved content: canonical JSON (sorted keys, no spaces) of `content` after "
                                  f"removing the export-only evidence fields {list(EXPORT_EVIDENCE_FIELDS)}"),
        "is_latest_version": target["version"] == latest["version"],
        "superseded_by_version": None if target["version"] == latest["version"] else latest["version"],
        "approval": {"decision": decision["decision"], "reviewer": decision["actor"],
                     "comment": decision["comment"], "decided_at": decision["decided_at"]},
        "exported_at": utcnow(),
        "content": enrich_evidence(conn, content),
        "evidence_warnings": evidence_warnings(conn, content),  # advisory; outside the hashed content
    }
