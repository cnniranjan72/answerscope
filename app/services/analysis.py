"""Analysis runs: classify every response in scope, score it, and persist an explicit
outcome per response together with a trace of every model call.

Bounded synchronous flow: the request returns when every response has an outcome.
Each response's result is committed in its own transaction, so a failure on one
record never discards results already stored for others.
"""
from __future__ import annotations

import json
import os
import sqlite3
import uuid
from dataclasses import asdict
from pathlib import Path

from app.config import Settings
from app.db import transaction, utcnow
from app.errors import NotFound, Unprocessable
from app.services import baseline, scoring
from app.services.analyzer import PROMPT_VERSION, AnalysisOutcome, analyse_response
from app.services.categories import CATEGORY_VERSION, is_branded, topic
from app.services.citations import CITATION_POLICY_VERSION, citation_features
from app.services.llm import CallRequest, OllamaProvider, Provider, ReplayProvider, StubProvider
from app.services.text import answer_body


def _stub_responder(req: CallRequest) -> str:
    user = req.messages[1]["content"]
    body = user.split("<<<ANSWER\n", 1)[1].rsplit("\nANSWER>>>", 1)[0]
    return baseline.classify_json(body)


def replay_dir(settings: Settings, version: str = PROMPT_VERSION) -> Path:
    return settings.replay_dir / version.replace("-", "_")


def build_provider(name: str, settings: Settings, stub_scenarios: dict[str, str] | None = None,
                   version: str = PROMPT_VERSION) -> Provider:
    if name == "ollama":
        return OllamaProvider(settings.ollama_url, settings.ollama_model, settings.model_timeout_s,
                              settings.model_max_output_tokens)
    if name == "replay":
        return ReplayProvider(replay_dir(settings, version))
    if name == "stub":
        return StubProvider(_stub_responder, stub_scenarios or {})
    raise Unprocessable(f"unknown provider {name!r}")


def _write_recording(directory: Path, response_id: str, model: str, outcome: AnalysisOutcome,
                     version: str = PROMPT_VERSION) -> None:
    """Atomic write (temp file + rename): an interrupted run never leaves a truncated
    recording that would break a later replay or be skipped by --only-unrecorded."""
    directory.mkdir(parents=True, exist_ok=True)
    rec = {"response_id": response_id, "prompt_version": version, "model": model,
           "input_sha256": outcome.input_sha256, "recorded_at": utcnow(),
           "attempts": [{"outcome": a.outcome, "error": a.error, "latency_ms": a.latency_ms,
                         "raw_output": a.raw_output} for a in outcome.attempts]}
    target = directory / f"{response_id}.json"
    tmp = target.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, target)


def run_analysis(conn: sqlite3.Connection, settings: Settings, provider: Provider, *, actor: str,
                 response_ids: list[str] | None = None, record_dir: Path | None = None,
                 progress=None, version: str = PROMPT_VERSION) -> str:
    rows = conn.execute(
        "SELECT r.response_id, r.prompt_id, r.engine, r.answer_text, p.text AS question "
        "FROM responses r JOIN prompts p USING (prompt_id) ORDER BY r.prompt_id, r.engine").fetchall()
    if response_ids is not None:
        wanted = set(response_ids)
        unknown = sorted(wanted - {r["response_id"] for r in rows})
        if unknown:
            raise Unprocessable("unknown response_ids", {"unknown": unknown[:50]})
        rows = [r for r in rows if r["response_id"] in wanted]
    if not rows:
        raise Unprocessable("no imported responses to analyse; import a dataset first")
    if len(rows) > settings.max_responses_per_analysis:
        raise Unprocessable(f"analysis limited to {settings.max_responses_per_analysis} responses")

    analysis_id = str(uuid.uuid4())
    config = {"max_attempts": settings.model_max_attempts, "timeout_s": settings.model_timeout_s,
              "max_output_tokens": settings.model_max_output_tokens,
              "max_input_chars": settings.max_input_chars, "citation_policy": CITATION_POLICY_VERSION,
              "score_weights": scoring.WEIGHTS}
    with transaction(conn):
        conn.execute(
            "INSERT INTO analysis_runs (analysis_id, status, provider, execution_mode, model, prompt_version, "
            "score_version, category_version, config_json, created_by, started_at) "
            "VALUES (?, 'running', ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (analysis_id, type(provider).__name__, provider.execution_mode, provider.model, version,
             scoring.SCORE_VERSION, CATEGORY_VERSION, json.dumps(config), actor, utcnow()))

    for i, r in enumerate(rows, start=1):
        _analyse_one(conn, settings, provider, analysis_id, r, record_dir, version)
        if progress:
            progress(i, len(rows), r["response_id"])

    counts = conn.execute("SELECT status, COUNT(*) AS n FROM response_results WHERE analysis_id = ? "
                          "GROUP BY status", (analysis_id,)).fetchall()
    counts = {c["status"]: c["n"] for c in counts}
    status = "completed" if not counts.get("failed") else (
        "completed_with_failures" if counts.get("succeeded") else "failed")
    with transaction(conn):
        conn.execute("UPDATE analysis_runs SET status = ?, finished_at = ?, counts_json = ?, model = ? "
                     "WHERE analysis_id = ?",
                     (status, utcnow(), json.dumps({"eligible": len(rows), **counts}), provider.model,
                      analysis_id))
    return analysis_id


def _analyse_one(conn, settings, provider, analysis_id, r, record_dir, version=PROMPT_VERSION) -> None:
    body = answer_body(r["answer_text"])
    cites = [dict(c) for c in conn.execute(
        "SELECT url, citation_type FROM citations WHERE response_id = ? ORDER BY ord", (r["response_id"],))]
    cfeat = citation_features(cites)
    base = dict(analysis_id=analysis_id, response_id=r["response_id"], engine=r["engine"],
                prompt_id=r["prompt_id"], branded=int(is_branded(r["question"])),
                category=topic(r["question"]), citations_json=json.dumps(cfeat))
    outcome = None
    if not body.strip():
        result = dict(status="skipped", reason="answer body is empty after removing the citation list")
    elif len(body) > settings.max_input_chars:
        result = dict(status="skipped", reason=f"answer body has {len(body)} chars, above MAX_INPUT_CHARS="
                      f"{settings.max_input_chars}; not truncated, because truncation could drop evidence")
    else:
        try:
            outcome = analyse_response(provider, response_id=r["response_id"], question=r["question"],
                                       body=body, max_attempts=settings.model_max_attempts, version=version)
        except Exception as e:  # an unexpected bug on one record must not abort the run
            outcome = AnalysisOutcome("failed", f"internal_error: {type(e).__name__}", None)
        if outcome.status == "succeeded":
            comp = scoring.components(outcome.labels["labels"], cfeat)
            result = dict(status="succeeded", reason=None, labels_json=json.dumps(outcome.labels),
                          components_json=json.dumps(comp), score=scoring.score(comp))
        else:
            result = dict(status="failed", reason=outcome.reason)
        if record_dir is not None and isinstance(provider, OllamaProvider):
            _write_recording(record_dir, r["response_id"], provider.model, outcome, version)

    row = {**base, "labels_json": None, "components_json": None, "score": None, **result,
           "attempts": len(outcome.attempts) if outcome else 0, "created_at": utcnow()}
    with transaction(conn):
        conn.execute(
            "INSERT INTO response_results (analysis_id, response_id, status, reason, engine, prompt_id, branded, "
            "category, labels_json, citations_json, components_json, score, attempts, created_at) VALUES "
            "(:analysis_id, :response_id, :status, :reason, :engine, :prompt_id, :branded, :category, "
            ":labels_json, :citations_json, :components_json, :score, :attempts, :created_at)", row)
        for a in (outcome.attempts if outcome else []):
            t = asdict(a)
            conn.execute(
                "INSERT INTO model_calls (analysis_id, response_id, attempt, execution_mode, model, prompt_version, "
                "input_sha256, outcome, error, latency_ms, raw_output, created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                (analysis_id, r["response_id"], t["attempt"], provider.execution_mode, provider.model,
                 version, outcome.input_sha256, t["outcome"], t["error"], t["latency_ms"],
                 t["raw_output"], utcnow()))


def result_rows(conn: sqlite3.Connection, analysis_id: str) -> list[dict]:
    out = []
    for r in conn.execute("SELECT * FROM response_results WHERE analysis_id = ? ORDER BY prompt_id, engine",
                          (analysis_id,)):
        d = dict(r)
        d["branded"] = bool(d["branded"])
        for k in ("labels_json", "citations_json", "components_json"):
            d[k.removesuffix("_json")] = json.loads(d.pop(k)) if d[k] else None
        out.append(d)
    return out


def get_run(conn: sqlite3.Connection, analysis_id: str) -> dict:
    run = conn.execute("SELECT * FROM analysis_runs WHERE analysis_id = ?", (analysis_id,)).fetchone()
    if run is None:
        raise NotFound(f"analysis {analysis_id} not found")
    d = dict(run)
    d["config"] = json.loads(d.pop("config_json"))
    d["counts"] = json.loads(d.pop("counts_json") or "{}")
    d["model_quality_note"] = _quality_note(d["execution_mode"])
    d["call_stats"] = call_stats(conn, analysis_id, d["execution_mode"])
    return d


def call_stats(conn: sqlite3.Connection, analysis_id: str, mode: str) -> dict:
    """Model calls, outcomes and time for this run (brief: record calls, time and cost).
    In replay mode the latencies are lookup times; the original model latencies are
    stored in the replay recordings."""
    rows = conn.execute("SELECT outcome, COUNT(*) AS n, SUM(latency_ms) AS ms FROM model_calls "
                        "WHERE analysis_id = ? GROUP BY outcome", (analysis_id,)).fetchall()
    total_ms = sum(r["ms"] or 0 for r in rows)
    calls = sum(r["n"] for r in rows)
    return {
        "calls": calls,
        "by_outcome": {r["outcome"]: r["n"] for r in rows},
        "total_call_seconds": round(total_ms / 1000, 1),
        "mean_call_seconds": round(total_ms / 1000 / calls, 2) if calls else None,
        "cost_usd": 0.0 if mode in ("local_model", "replay", "stub") else None,
        "cost_note": {"local_model": "local Ollama model; no API charges (electricity/GPU time not costed)",
                      "replay": "no model calls; replayed recordings",
                      "stub": "no model calls; deterministic stub"}.get(mode, "not measured"),
    }


def _quality_note(mode: str) -> str:
    return {
        "local_model": "Labels from a real local model run (one run; no repeated-run variance measured).",
        "replay": "Replayed outputs recorded from an earlier local-model run; demonstrates mechanics and "
                  "reproduces that run's labels. Not a fresh model call.",
        "stub": "STUB: deterministic baseline output for engineering tests. Not evidence of model quality.",
    }.get(mode, "")
