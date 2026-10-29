"""HTTP routes. Handlers stay thin: authorisation via dependencies, logic in services."""
from __future__ import annotations

import json
import sqlite3
from typing import Iterator

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import PlainTextResponse

from app.config import Identity
from app.db import connect
from app.errors import Conflict, NotFound
from app.schemas import AnalysisCreate, DatasetImport, DecisionRequest, ReportCreate, ReportPatch, SubmitRequest
from app.security import current_identity, require
from app.services import analysis, ingestion, reporting, review, scoring
from app.services.claims import CLAIM_CHECK_VERSION

router = APIRouter()
ANALYST = require("analyst")
REVIEWER = require("reviewer")


def db(request: Request) -> Iterator[sqlite3.Connection]:
    conn = connect(request.app.state.settings.db_path)
    try:
        yield conn
    finally:
        conn.close()


@router.get("/health", tags=["system"])
def health(request: Request, conn: sqlite3.Connection = Depends(db)):
    conn.execute("SELECT 1").fetchone()
    s = request.app.state.settings
    return {"status": "ok", "database": "ok", "default_provider": s.provider,
            "versions": {"prompt": analysis.PROMPT_VERSION, "score": scoring.SCORE_VERSION,
                         "category": analysis.CATEGORY_VERSION, "citation_policy": analysis.CITATION_POLICY_VERSION,
                         "report_generator": reporting.REPORT_GENERATOR_VERSION,
                         "evidence_policy": reporting.EVIDENCE_POLICY_VERSION, "claim_check": CLAIM_CHECK_VERSION}}


@router.get("/whoami", tags=["system"])
def whoami(identity: Identity = Depends(current_identity)):
    return {"name": identity.name, "role": identity.role}


# ---- datasets ---------------------------------------------------------------------------
@router.post("/datasets", status_code=201, tags=["datasets"],
             summary="Import prompt/response/citation records (validated per record, idempotent)")
def import_dataset(body: DatasetImport, actor: Identity = Depends(ANALYST), conn=Depends(db)):
    return ingestion.import_records(conn, body.model_dump(), actor=actor.name, source="api_records")


@router.post("/datasets/pack", status_code=201, tags=["datasets"],
             summary="Import the server-configured assignment pack (PACK_DIR); no client-supplied paths")
def import_pack(request: Request, actor: Identity = Depends(ANALYST), conn=Depends(db)):
    payload = ingestion.load_pack(request.app.state.settings.pack_dir)
    return ingestion.import_records(conn, payload, actor=actor.name, source="configured_pack")


@router.get("/datasets/{dataset_id}", tags=["datasets"])
def get_dataset(dataset_id: str, _: Identity = Depends(current_identity), conn=Depends(db)):
    row = conn.execute("SELECT * FROM datasets WHERE dataset_id = ?", (dataset_id,)).fetchone()
    if row is None:
        raise NotFound(f"dataset {dataset_id} not found")
    rejected = [dict(r) for r in conn.execute(
        "SELECT record_type, record_index, record_id, reason FROM dataset_records "
        "WHERE dataset_id = ? AND outcome = 'rejected' LIMIT 200", (dataset_id,))]
    return {**{k: row[k] for k in ("dataset_id", "source", "created_by", "created_at")},
            **json.loads(row["summary_json"]), "rejections": rejected}


# ---- analyses ---------------------------------------------------------------------------
@router.post("/analyses", status_code=201, tags=["analyses"],
             summary="Run analysis synchronously (bounded); every response gets an explicit outcome")
def create_analysis(body: AnalysisCreate, request: Request, actor: Identity = Depends(ANALYST), conn=Depends(db)):
    s = request.app.state.settings
    provider = analysis.build_provider(body.provider or s.provider, s)
    analysis_id = analysis.run_analysis(conn, s, provider, actor=actor.name, response_ids=body.response_ids)
    return analysis.get_run(conn, analysis_id)


@router.get("/analyses", tags=["analyses"])
def list_analyses(_: Identity = Depends(current_identity), conn=Depends(db)):
    rows = conn.execute("SELECT analysis_id, status, execution_mode, model, prompt_version, score_version, "
                        "started_at, finished_at, counts_json FROM analysis_runs ORDER BY started_at DESC")
    return {"analyses": [{**{k: r[k] for k in r.keys() if k != "counts_json"},
                          "counts": json.loads(r["counts_json"] or "{}")} for r in rows]}


@router.get("/analyses/{analysis_id}", tags=["analyses"], summary="Status, counts and aggregate scores")
def get_analysis(analysis_id: str, _: Identity = Depends(current_identity), conn=Depends(db)):
    run = analysis.get_run(conn, analysis_id)
    run["summary"] = scoring.aggregate(analysis.result_rows(conn, analysis_id))
    return run


@router.get("/analyses/{analysis_id}/results", tags=["analyses"], summary="Per-response results with evidence")
def get_results(analysis_id: str, status: str | None = Query(None, pattern="^(succeeded|failed|skipped)$"),
                engine: str | None = Query(None, pattern="^(aimode|chatgpt|gemini)$"),
                _: Identity = Depends(current_identity), conn=Depends(db)):
    analysis.get_run(conn, analysis_id)
    rows = [r for r in analysis.result_rows(conn, analysis_id)
            if (status is None or r["status"] == status) and (engine is None or r["engine"] == engine)]
    return {"analysis_id": analysis_id, "count": len(rows), "results": rows}


@router.get("/analyses/{analysis_id}/results/{response_id}/trace", tags=["analyses"],
            summary="Model call attempts for one response (mode, model, prompt version, raw output)")
def get_trace(analysis_id: str, response_id: str, _: Identity = Depends(current_identity), conn=Depends(db)):
    calls = [dict(r) for r in conn.execute(
        "SELECT * FROM model_calls WHERE analysis_id = ? AND response_id = ? ORDER BY attempt",
        (analysis_id, response_id))]
    res = conn.execute("SELECT status, reason FROM response_results WHERE analysis_id = ? AND response_id = ?",
                       (analysis_id, response_id)).fetchone()
    if res is None:
        raise NotFound("no result for that analysis/response")
    return {"analysis_id": analysis_id, "response_id": response_id, **dict(res), "calls": calls}


# ---- reports ----------------------------------------------------------------------------
@router.post("/reports", status_code=201, tags=["reports"], summary="Create a draft report from an analysis")
def create_report(body: ReportCreate, actor: Identity = Depends(ANALYST), conn=Depends(db)):
    return review.create_report(conn, body.analysis_id, actor)


@router.get("/reports", tags=["reports"])
def list_reports(_: Identity = Depends(current_identity), conn=Depends(db)):
    rows = conn.execute(
        "SELECT r.report_id, r.analysis_id, r.created_at, v.version AS latest_version, v.status AS latest_status, "
        "a.prompt_version, json_extract(v.content_json, '$.provenance.report_generator') AS report_generator "
        "FROM reports r JOIN report_versions v ON v.report_id = r.report_id AND v.version = "
        "(SELECT MAX(version) FROM report_versions WHERE report_id = r.report_id) "
        "LEFT JOIN analysis_runs a ON a.analysis_id = r.analysis_id ORDER BY r.created_at DESC")
    return {"reports": [dict(r) for r in rows]}


@router.get("/reports/{report_id}", tags=["reports"], summary="Report with version history, decisions, latest content")
def get_report(report_id: str, _: Identity = Depends(current_identity), conn=Depends(db)):
    return review.get_report(conn, report_id)


@router.get("/reports/{report_id}/compare", tags=["reports"],
            summary="Compare with another report: method vs data changes, rate changes with interval overlap")
def compare_report(report_id: str, against: str = Query(..., description="base report id, e.g. the approved one"),
                   _: Identity = Depends(current_identity), conn=Depends(db)):
    return review.compare_reports(conn, against, report_id)


@router.get("/reports/{report_id}/versions/{version}", tags=["reports"])
def get_version(report_id: str, version: int, _: Identity = Depends(current_identity), conn=Depends(db)):
    return review.get_version(conn, report_id, version)


@router.patch("/reports/{report_id}", tags=["reports"],
              summary="Edit the latest draft; editing a frozen version creates a new draft")
def patch_report(report_id: str, body: ReportPatch, actor: Identity = Depends(ANALYST), conn=Depends(db)):
    return review.patch_report(conn, report_id, body, actor)


@router.post("/reports/{report_id}/submit", tags=["review"], summary="Freeze a draft version for review")
def submit(report_id: str, body: SubmitRequest, request: Request, actor: Identity = Depends(ANALYST),
           conn=Depends(db)):
    return review.submit(conn, report_id, body.version, actor, request.app.state.settings.review_due_hours)


@router.post("/reports/{report_id}/decision", tags=["review"],
             summary="Approve or reject a submitted version (reviewer only, comment required)")
def decision(report_id: str, body: DecisionRequest, actor: Identity = Depends(REVIEWER), conn=Depends(db)):
    return review.decide(conn, report_id, body, actor)


@router.get("/reports/{report_id}/export", tags=["review"],
            summary="Export an approved version (default: latest; older approved versions only by explicit number)")
def export(report_id: str, version: int | None = Query(None, ge=1), _: Identity = Depends(current_identity),
           conn=Depends(db)):
    return review.export(conn, report_id, version)


@router.get("/reports/{report_id}/export.md", tags=["review"], response_class=PlainTextResponse,
            summary="The same approved export, rendered as a readable Markdown report (verified before rendering)")
def export_markdown(report_id: str, version: int | None = Query(None, ge=1), _: Identity = Depends(current_identity),
                    conn=Depends(db)):
    from app.render_export import render
    from app.verify_export import verify
    doc = json.loads(json.dumps(review.export(conn, report_id, version)))
    failed = [n for n, ok, _ in verify(doc) if not ok]
    if failed:
        raise Conflict("export did not verify; not rendered", {"failed_checks": failed}, code="integrity_error")
    return PlainTextResponse(render(doc), media_type="text/markdown; charset=utf-8", headers={
        "Content-Disposition": f'attachment; filename="report-{report_id[:8]}-v{doc["version"]}.md"'})
