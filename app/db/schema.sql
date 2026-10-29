-- AnswerScope SQLite schema (schema version 1).
-- Raw inputs are stored verbatim (raw_json) next to typed columns; IDs are the
-- supplied IDs, unchanged. Unknown values stay NULL.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS datasets (
    dataset_id      TEXT PRIMARY KEY,
    source          TEXT NOT NULL,            -- 'api_records' | 'configured_pack'
    created_by      TEXT NOT NULL,
    created_at      TEXT NOT NULL,
    summary_json    TEXT NOT NULL             -- counts per record type and outcome
);

-- Per-record import ledger: every submitted record gets an explicit outcome.
CREATE TABLE IF NOT EXISTS dataset_records (
    dataset_id      TEXT NOT NULL REFERENCES datasets(dataset_id),
    record_type     TEXT NOT NULL CHECK (record_type IN ('prompt', 'response', 'citation', 'unknown')),
    record_index    INTEGER NOT NULL,
    record_id       TEXT,
    outcome         TEXT NOT NULL CHECK (outcome IN ('inserted', 'reused', 'rejected')),
    reason          TEXT,
    PRIMARY KEY (dataset_id, record_type, record_index)
);

CREATE TABLE IF NOT EXISTS prompts (
    prompt_id       TEXT PRIMARY KEY,
    run_id          TEXT NOT NULL,
    text            TEXT NOT NULL,
    raw_json        TEXT NOT NULL,
    content_sha256  TEXT NOT NULL,
    first_dataset_id TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS responses (
    response_id     TEXT PRIMARY KEY,
    prompt_id       TEXT NOT NULL REFERENCES prompts(prompt_id),
    run_id          TEXT NOT NULL,
    engine          TEXT NOT NULL CHECK (engine IN ('aimode', 'chatgpt', 'gemini')),
    engine_name     TEXT,
    model_version   TEXT,
    answer_text     TEXT NOT NULL,
    answer_markdown TEXT,
    capture_status  TEXT NOT NULL,
    provider_timestamp TEXT,
    archive_stored_at TEXT,
    settings_json   TEXT,
    raw_json        TEXT NOT NULL,
    content_sha256  TEXT NOT NULL,
    first_dataset_id TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS citations (
    citation_id     TEXT PRIMARY KEY,
    response_id     TEXT NOT NULL REFERENCES responses(response_id),
    prompt_id       TEXT NOT NULL,
    engine          TEXT NOT NULL,
    ord             INTEGER NOT NULL,
    citation_type   TEXT NOT NULL,
    url             TEXT NOT NULL,
    normalized_url  TEXT NOT NULL,
    host            TEXT NOT NULL,
    title           TEXT,
    publication_date TEXT,
    raw_json        TEXT NOT NULL,
    content_sha256  TEXT NOT NULL,
    first_dataset_id TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_citations_response ON citations(response_id);

CREATE TABLE IF NOT EXISTS analysis_runs (
    analysis_id     TEXT PRIMARY KEY,
    status          TEXT NOT NULL CHECK (status IN ('running', 'completed', 'completed_with_failures', 'failed')),
    provider        TEXT NOT NULL,
    execution_mode  TEXT NOT NULL CHECK (execution_mode IN ('live', 'local_model', 'replay', 'stub')),
    model           TEXT NOT NULL,
    prompt_version  TEXT NOT NULL,
    score_version   TEXT NOT NULL,
    category_version TEXT NOT NULL,
    config_json     TEXT NOT NULL,
    created_by      TEXT NOT NULL,
    started_at      TEXT NOT NULL,
    finished_at     TEXT,
    counts_json     TEXT
);

-- One row per (analysis, response): succeeded, failed or skipped, never missing.
CREATE TABLE IF NOT EXISTS response_results (
    analysis_id     TEXT NOT NULL REFERENCES analysis_runs(analysis_id),
    response_id     TEXT NOT NULL REFERENCES responses(response_id),
    status          TEXT NOT NULL CHECK (status IN ('succeeded', 'failed', 'skipped')),
    reason          TEXT,
    engine          TEXT NOT NULL,
    prompt_id       TEXT NOT NULL,
    branded         INTEGER NOT NULL,
    category        TEXT NOT NULL,
    labels_json     TEXT,       -- labels + verified evidence spans (NULL unless succeeded)
    citations_json  TEXT,       -- deterministic citation features
    components_json TEXT,       -- score components (NULL unless succeeded)
    score           REAL,       -- NULL unless succeeded: a failure is not a zero
    attempts        INTEGER NOT NULL DEFAULT 0,
    created_at      TEXT NOT NULL,
    PRIMARY KEY (analysis_id, response_id)
);

-- Trace of every model call attempt.
CREATE TABLE IF NOT EXISTS model_calls (
    call_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id     TEXT NOT NULL,
    response_id     TEXT NOT NULL,
    attempt         INTEGER NOT NULL,
    execution_mode  TEXT NOT NULL,
    model           TEXT NOT NULL,
    prompt_version  TEXT NOT NULL,
    input_sha256    TEXT NOT NULL,
    outcome         TEXT NOT NULL,   -- ok | timeout | provider_error | empty | malformed | invalid | replay_missing
    error           TEXT,
    latency_ms      INTEGER,
    raw_output      TEXT,            -- truncated to a bounded size
    created_at      TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_calls_analysis ON model_calls(analysis_id, response_id);

CREATE TABLE IF NOT EXISTS reports (
    report_id       TEXT PRIMARY KEY,
    analysis_id     TEXT NOT NULL REFERENCES analysis_runs(analysis_id),
    created_by      TEXT NOT NULL,
    created_at      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS report_versions (
    report_id       TEXT NOT NULL REFERENCES reports(report_id),
    version         INTEGER NOT NULL,
    status          TEXT NOT NULL CHECK (status IN ('draft', 'submitted', 'approved', 'rejected')),
    content_json    TEXT NOT NULL,
    content_sha256  TEXT NOT NULL,
    parent_version  INTEGER,
    created_by      TEXT NOT NULL,
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL,
    submitted_by    TEXT,
    submitted_at    TEXT,
    review_due_at   TEXT,  -- set on submit; overdue versions are flagged, never auto-approved
    PRIMARY KEY (report_id, version)
);

CREATE TABLE IF NOT EXISTS review_decisions (
    decision_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id       TEXT NOT NULL,
    version         INTEGER NOT NULL,
    decision        TEXT NOT NULL CHECK (decision IN ('approved', 'rejected')),
    comment         TEXT NOT NULL CHECK (length(trim(comment)) > 0),
    actor           TEXT NOT NULL,
    actor_role      TEXT NOT NULL CHECK (actor_role = 'reviewer'),
    content_sha256  TEXT NOT NULL,
    decided_at      TEXT NOT NULL,
    UNIQUE (report_id, version),
    FOREIGN KEY (report_id, version) REFERENCES report_versions(report_id, version)
);

-- Defence in depth: the database itself refuses to alter frozen content.
CREATE TRIGGER IF NOT EXISTS trg_frozen_content
BEFORE UPDATE OF content_json, content_sha256 ON report_versions
WHEN OLD.status <> 'draft'
BEGIN
    SELECT RAISE(ABORT, 'report version is frozen');
END;

CREATE TRIGGER IF NOT EXISTS trg_status_transition
BEFORE UPDATE OF status ON report_versions
WHEN NOT ((OLD.status = 'draft' AND NEW.status = 'submitted')
       OR (OLD.status = 'submitted' AND NEW.status IN ('approved', 'rejected')))
BEGIN
    SELECT RAISE(ABORT, 'invalid report status transition');
END;

CREATE TRIGGER IF NOT EXISTS trg_no_delete_versions
BEFORE DELETE ON report_versions
BEGIN
    SELECT RAISE(ABORT, 'report versions are append-only');
END;

CREATE TRIGGER IF NOT EXISTS trg_decisions_immutable_u
BEFORE UPDATE ON review_decisions
BEGIN
    SELECT RAISE(ABORT, 'review decisions are immutable');
END;

CREATE TRIGGER IF NOT EXISTS trg_decisions_immutable_d
BEFORE DELETE ON review_decisions
BEGIN
    SELECT RAISE(ABORT, 'review decisions are immutable');
END;
