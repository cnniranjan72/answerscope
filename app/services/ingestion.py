"""Validated, idempotent import.

Duplicate policy: records are keyed by their supplied ID. Re-importing an identical
record (same canonical SHA-256) is *reused* - no new row. The same ID with different
content is *rejected* as a conflict and the stored record is kept. Every submitted
record gets an outcome (inserted / reused / rejected + reason) in the dataset ledger,
so nothing is silently dropped or duplicated, and one bad record never blocks the rest.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import uuid
from pathlib import Path

from pydantic import ValidationError

from app.db import transaction, utcnow
from app.schemas import CitationRecord, PromptRecord, ResponseRecord
from app.services.citations import host_of, normalise_url

MAX_REJECTIONS_RETURNED = 100


def canonical_sha(record: dict) -> str:
    return hashlib.sha256(json.dumps(record, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    """Malformed lines become an explicit placeholder that validation will reject."""
    out = []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
            out.append(obj if isinstance(obj, dict) else {"__invalid__": f"line {n}: not a JSON object"})
        except json.JSONDecodeError as e:
            out.append({"__invalid__": f"line {n}: invalid JSON ({e.msg})"})
    return out


def load_pack(pack_dir: Path) -> dict[str, list[dict]]:
    data = pack_dir / "data"
    return {name: read_jsonl(data / f"{name}.jsonl") for name in ("prompts", "responses", "citations")}


def _reason(e: ValidationError) -> str:
    return "; ".join(f"{'.'.join(map(str, err['loc'])) or 'record'}: {err['msg']}" for err in e.errors()[:5])


def import_records(conn: sqlite3.Connection, payload: dict[str, list[dict]], *, actor: str,
                   source: str) -> dict:
    dataset_id = str(uuid.uuid4())
    counts = {t: {"submitted": 0, "inserted": 0, "reused": 0, "rejected": 0}
              for t in ("prompts", "responses", "citations")}
    rejections: list[dict] = []
    ledger: list[tuple] = []

    def record(kind: str, rtype: str, idx: int, rid: str | None, outcome: str, reason: str | None = None):
        counts[kind][outcome] += 1
        ledger.append((dataset_id, rtype, idx, rid, outcome, reason))
        if outcome == "rejected" and len(rejections) < MAX_REJECTIONS_RETURNED:
            rejections.append({"record_type": rtype, "index": idx, "id": rid, "reason": reason})

    def existing_sha(table: str, key: str, rid: str) -> str | None:
        row = conn.execute(f"SELECT content_sha256 FROM {table} WHERE {key} = ?", (rid,)).fetchone()
        return row["content_sha256"] if row else None

    with transaction(conn):
        conn.execute("INSERT INTO datasets VALUES (?, ?, ?, ?, ?)",
                     (dataset_id, source, actor, utcnow(), "{}"))

        specs = [
            ("prompts", "prompt", PromptRecord, "prompt_id"),
            ("responses", "response", ResponseRecord, "response_id"),
            ("citations", "citation", CitationRecord, "citation_id"),
        ]
        for kind, rtype, model, key in specs:
            for idx, raw in enumerate(payload.get(kind, [])):
                counts[kind]["submitted"] += 1
                rid = raw.get(key) if isinstance(raw, dict) and isinstance(raw.get(key), str) else None
                if not isinstance(raw, dict) or "__invalid__" in raw:
                    record(kind, rtype, idx, rid, "rejected",
                           raw.get("__invalid__") if isinstance(raw, dict) else "not a JSON object")
                    continue
                try:
                    rec = model.model_validate(raw)
                except ValidationError as e:
                    record(kind, rtype, idx, rid, "rejected", _reason(e))
                    continue
                sha = canonical_sha(raw)
                prior = existing_sha(f"{kind}", key, rid)
                if prior is not None:
                    if prior == sha:
                        record(kind, rtype, idx, rid, "reused")
                    else:
                        record(kind, rtype, idx, rid, "rejected",
                               "conflict: same ID already imported with different content")
                    continue
                problem = _insert(conn, rtype, rec, raw, sha, dataset_id)
                if problem:
                    record(kind, rtype, idx, rid, "rejected", problem)
                else:
                    record(kind, rtype, idx, rid, "inserted")

        conn.executemany("INSERT INTO dataset_records VALUES (?, ?, ?, ?, ?, ?)", ledger)
        summary = {"counts": counts}
        conn.execute("UPDATE datasets SET summary_json = ? WHERE dataset_id = ?",
                     (json.dumps(summary), dataset_id))
    return {"dataset_id": dataset_id, "source": source, "counts": counts,
            "rejections": rejections, "rejections_truncated": sum(c["rejected"] for c in counts.values())
            > len(rejections)}


def _insert(conn: sqlite3.Connection, rtype: str, rec, raw: dict, sha: str, dataset_id: str) -> str | None:
    """Insert one validated record; returns a rejection reason for broken references."""
    raw_json = json.dumps(raw, ensure_ascii=False)
    if rtype == "prompt":
        conn.execute("INSERT INTO prompts VALUES (?, ?, ?, ?, ?, ?)",
                     (rec.prompt_id, rec.run_id, rec.text, raw_json, sha, dataset_id))
        return None
    if rtype == "response":
        prompt = conn.execute("SELECT run_id FROM prompts WHERE prompt_id = ?", (rec.prompt_id,)).fetchone()
        if prompt is None:
            return f"unknown prompt_id {rec.prompt_id!r}"
        if prompt["run_id"] != rec.run_id:
            return "run_id differs from its prompt's run_id"
        conn.execute(
            "INSERT INTO responses VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (rec.response_id, rec.prompt_id, rec.run_id, rec.engine, rec.engine_name, rec.model_version,
             rec.answer_text, rec.answer_markdown, rec.capture_status, rec.provider_timestamp,
             rec.archive_stored_at, json.dumps(rec.settings) if rec.settings is not None else None,
             raw_json, sha, dataset_id))
        return None
    resp = conn.execute("SELECT prompt_id, engine FROM responses WHERE response_id = ?",
                        (rec.response_id,)).fetchone()
    if resp is None:
        return f"unknown response_id {rec.response_id!r}"
    if (resp["prompt_id"], resp["engine"]) != (rec.prompt_id, rec.engine):
        return "prompt_id/engine do not match the referenced response"
    conn.execute(
        "INSERT INTO citations VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (rec.citation_id, rec.response_id, rec.prompt_id, rec.engine, rec.order, rec.citation_type,
         rec.url, normalise_url(rec.url), host_of(rec.url), rec.title, rec.publication_date,
         raw_json, sha, dataset_id))
    return None
