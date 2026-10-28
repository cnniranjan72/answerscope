"""Validated contracts: supplied input records (mirrors schemas/input_contract.json)
and API request bodies. Request bodies forbid unknown fields, so a caller cannot slip
in an 'actor' or 'role'; identity comes only from the bearer token."""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

Engine = Literal["aimode", "chatgpt", "gemini"]
NonEmpty = Field(min_length=1, max_length=200)


class PromptRecord(BaseModel):
    model_config = ConfigDict(extra="allow")
    prompt_id: str = NonEmpty
    run_id: str = NonEmpty
    text: str = Field(min_length=1, max_length=5_000)


class ResponseRecord(BaseModel):
    model_config = ConfigDict(extra="allow")
    response_id: str = NonEmpty
    run_id: str = NonEmpty
    prompt_id: str = NonEmpty
    engine: Engine
    engine_name: str | None = None
    model_version: str | None = None
    answer_text: str = Field(min_length=1, max_length=200_000)
    answer_markdown: str | None = None
    capture_status: Literal["captured"]
    provider_timestamp: str | None = None
    archive_stored_at: str | None = None
    settings: dict[str, Any] | None = None

    @field_validator("answer_text")
    @classmethod
    def not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("answer_text is blank")
        return v


class CitationRecord(BaseModel):
    model_config = ConfigDict(extra="allow")
    citation_id: str = NonEmpty
    response_id: str = NonEmpty
    prompt_id: str = NonEmpty
    engine: Engine
    order: int = Field(ge=1)
    citation_type: Literal["inline_hyperlink", "sources_panel"]
    url: str = Field(min_length=1, max_length=4_000)
    title: str | None = None
    publication_date: str | None = None

    @field_validator("url")
    @classmethod
    def http_url(cls, v: str) -> str:
        if not v.lower().startswith(("http://", "https://")):
            raise ValueError("url must be http(s)")
        return v


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class DatasetImport(Strict):
    """Records are validated one by one so a bad record cannot block valid ones."""
    prompts: list[dict[str, Any]] = Field(default_factory=list, max_length=1_000)
    responses: list[dict[str, Any]] = Field(default_factory=list, max_length=5_000)
    citations: list[dict[str, Any]] = Field(default_factory=list, max_length=50_000)


class AnalysisCreate(Strict):
    provider: Literal["replay", "stub", "ollama"] | None = Field(
        default=None, description="Defaults to server MODEL_PROVIDER.")
    response_ids: list[str] | None = Field(default=None, max_length=500,
                                           description="Optional subset; default all imported responses.")


class ReportCreate(Strict):
    analysis_id: str


class Evidence(Strict):
    response_id: str = Field(min_length=1, max_length=100)
    quote: str = Field(min_length=3, max_length=1_000)


class Diagnostic(Strict):
    id: str = Field(pattern=r"^D[1-9]$")
    priority: int = Field(ge=1, le=9)
    title: str = Field(min_length=3, max_length=200)
    kind: Literal["loss", "win", "risk"]
    observation: str = Field(min_length=10, max_length=3_000)
    hypothesis: str = Field(min_length=10, max_length=2_000)
    how_to_test: str = Field(min_length=10, max_length=2_000)
    metrics: dict[str, Any] = Field(default_factory=dict)
    evidence: list[Evidence] = Field(min_length=1, max_length=12)


class Remedy(Strict):
    id: str = Field(pattern=r"^R[1-9]$")
    priority: int = Field(ge=1, le=9)
    diagnostic_id: str = Field(pattern=r"^D[1-9]$")
    problem: str = Field(min_length=10, max_length=2_000)
    evidence: list[Evidence] = Field(min_length=1, max_length=12)
    action: str = Field(min_length=10, max_length=3_000)
    expected_benefit: str = Field(min_length=10, max_length=1_000)
    effort: Literal["low", "medium", "high"]
    effort_detail: str = Field(min_length=3, max_length=500)
    uncertainty: str = Field(min_length=10, max_length=1_000)
    validation: str = Field(min_length=10, max_length=1_500)


class ReportPatch(Strict):
    base_version: int = Field(ge=1, description="Version the analyst edited; must be the latest.")
    title: str | None = Field(default=None, min_length=3, max_length=200)
    executive_summary: str | None = Field(default=None, max_length=5_000)
    diagnostics: list[Diagnostic] | None = Field(default=None, max_length=9)
    remedies: list[Remedy] | None = Field(default=None, max_length=9)
    analyst_notes: str | None = Field(default=None, max_length=5_000)


class SubmitRequest(Strict):
    version: int = Field(ge=1)


class DecisionRequest(Strict):
    version: int = Field(ge=1)
    decision: Literal["approve", "reject"]
    comment: str = Field(min_length=3, max_length=5_000)
    content_sha256: str = Field(pattern=r"^[0-9a-f]{64}$",
                                description="Hash of the exact version content the reviewer read.")
