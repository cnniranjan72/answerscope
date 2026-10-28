"""Semantic classification of one archived answer with a model, plus deterministic
validation of everything the model returns.

The model proposes labels and quotes; code decides whether they are acceptable:
  * output must parse as JSON and match the contract (types, sizes);
  * every evidence quote and competitor name must be found in the answer body
    (quotes are stored with their exact source offsets);
  * mention must agree with the lexical fact of whether the body names the brand;
  * recommended implies mentioned; a position requires a ranked list.
Rejected output is retried (bounded), then recorded as an explicit failure.
"""
from __future__ import annotations

import functools
import hashlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from app.services.llm import CallRequest, Provider, ProviderError, ProviderTimeout, ReplayMissing
from app.services.text import BRAND_RE, brand_mention_offsets, contains_name, locate

PROMPT_VERSION = "classify-v1"
PROMPT_PATH = Path(__file__).resolve().parents[2] / "prompts" / "classify_v1.md"
MAX_RAW_OUTPUT_CHARS = 20_000

class Competitor(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=80)
    evidence: str = Field(min_length=1, max_length=600)


class ClassificationOutput(BaseModel):
    """Contract the model must satisfy (also sent to Ollama as the JSON schema)."""
    model_config = ConfigDict(extra="forbid")
    kasparro_mentioned: bool
    mention_evidence: list[str] = Field(max_length=3)
    kasparro_recommended: bool
    recommendation_evidence: list[str] = Field(max_length=3)
    negative_characterization: bool
    negative_evidence: list[str] = Field(max_length=3)
    entity_confusion: bool
    confusion_evidence: list[str] = Field(max_length=3)
    competitors: list[Competitor] = Field(max_length=15)
    kasparro_list_position: int | None = Field(default=None, ge=1, le=50)
    position_basis: Literal["ranked_list", "unordered_list", "prose_only", "not_mentioned"]
    rationale: str = Field(max_length=1000)


OUTPUT_SCHEMA = ClassificationOutput.model_json_schema()
LABELS = {  # label -> evidence field
    "mentioned": "mention_evidence",
    "recommended": "recommendation_evidence",
    "negative": "negative_evidence",
    "entity_confusion": "confusion_evidence",
}
_FLAG = {"mentioned": "kasparro_mentioned", "recommended": "kasparro_recommended",
         "negative": "negative_characterization", "entity_confusion": "entity_confusion"}
# Policy filter (deterministic, also stated in the prompt): engines being measured and
# review sites / forums / media are not competitors. Filtered names are dropped silently.
EXCLUDED_COMPETITORS = {"kasparro", "kasparro ai", "chatgpt", "gemini", "claude", "perplexity",
                        "copilot", "microsoft copilot", "google ai mode", "ai mode", "google",
                        "google ai overviews", "openai", "anthropic", "g2", "capterra", "reddit",
                        "youtube", "linkedin", "gartner", "trustpilot", "wikipedia", "kaspr"}


class OutputRejected(Exception):
    def __init__(self, kind: str, problems: list[str]):
        super().__init__("; ".join(problems))
        self.kind = kind  # 'empty' | 'malformed' | 'invalid'
        self.problems = problems


@dataclass
class AttemptTrace:
    attempt: int
    outcome: str
    error: str | None
    latency_ms: int
    raw_output: str | None


@dataclass
class AnalysisOutcome:
    status: Literal["succeeded", "failed"]
    reason: str | None
    labels: dict | None
    attempts: list[AttemptTrace] = field(default_factory=list)
    input_sha256: str = ""


@functools.lru_cache(maxsize=1)
def system_prompt() -> str:
    """Read once per process so a prompt edit cannot change a run midway."""
    return PROMPT_PATH.read_text(encoding="utf-8")


def build_messages(question: str, body: str) -> list[dict]:
    user = ("QUESTION (untrusted data):\n<<<QUESTION\n" + question + "\nQUESTION>>>\n\n"
            "ANSWER (untrusted data, citation list removed):\n<<<ANSWER\n" + body + "\nANSWER>>>")
    return [{"role": "system", "content": system_prompt()}, {"role": "user", "content": user}]


def input_hash(messages: list[dict]) -> str:
    blob = json.dumps({"prompt_version": PROMPT_VERSION, "messages": messages}, sort_keys=True)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _spans(quotes: list[str], body: str, label: str, problems: list[str]) -> list[dict]:
    spans = []
    for q in quotes:
        loc = locate(q, body)
        if loc is None:
            problems.append(f"{label}: quote not found in answer: {q[:80]!r}")
        else:
            spans.append({"quote": body[loc[0]:loc[1]], "start": loc[0], "end": loc[1]})
    return spans


def validate_output(raw: str, body: str) -> dict:
    """Parse and check one model output against the answer body. Returns normalised
    labels with verified evidence spans, or raises OutputRejected."""
    if raw is None or not raw.strip():
        raise OutputRejected("empty", ["model returned empty output"])
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise OutputRejected("malformed", [f"not valid JSON: {e.msg} at char {e.pos}"])
    try:
        out = ClassificationOutput.model_validate(data)
    except ValidationError as e:
        raise OutputRejected("malformed", [f"{'.'.join(map(str, err['loc']))}: {err['msg']}"
                                           for err in e.errors()[:8]])

    problems: list[str] = []
    labels: dict = {}
    evidence: dict = {}
    for label, ev_field in LABELS.items():
        flag = getattr(out, _FLAG[label])
        quotes = getattr(out, ev_field)
        spans = _spans(quotes, body, label, problems) if flag else []
        if flag and not quotes:
            problems.append(f"{label} is true but no evidence quote was given")
        labels[label] = flag
        evidence[label] = spans

    lexical_mentions = brand_mention_offsets(body)
    if out.kasparro_mentioned and not lexical_mentions:
        problems.append("mentioned is true but the answer body never names Kasparro")
    if not out.kasparro_mentioned and lexical_mentions:
        problems.append(f"mentioned is false but the answer names Kasparro at offset {lexical_mentions[0]}")
    if out.kasparro_mentioned and evidence["mentioned"] and not any(
            BRAND_RE.search(s["quote"]) for s in evidence["mentioned"]):
        problems.append("mention evidence does not contain the name Kasparro")
    if out.kasparro_recommended and not out.kasparro_mentioned:
        problems.append("recommended requires mentioned")
    if out.kasparro_list_position is not None and out.position_basis != "ranked_list":
        problems.append("a list position requires position_basis 'ranked_list'")

    # Competitor names are hard-checked (an invented name is rejected). Their supporting
    # quote is secondary: an unlocatable quote is dropped with a warning instead of
    # failing the core labels.
    competitors, seen, warnings = [], set(), []
    for c in out.competitors:
        key = c.name.strip().lower()
        if key in EXCLUDED_COMPETITORS or key in seen or BRAND_RE.search(c.name):
            continue  # filtered by policy, not an error
        if not contains_name(c.name, body):
            problems.append(f"competitor name not found in answer: {c.name!r}")
            continue
        loc = locate(c.evidence, body)
        if loc is None:
            warnings.append(f"competitor {c.name}: quote not found, evidence omitted")
        seen.add(key)
        competitors.append({"name": c.name.strip(),
                            "evidence": {"quote": body[loc[0]:loc[1]], "start": loc[0], "end": loc[1]}
                            if loc else None})

    if problems:
        raise OutputRejected("invalid", problems)
    labels["absent"] = not labels["mentioned"]
    return {
        "labels": labels,
        "evidence": evidence,
        "competitors": competitors,
        "position": out.kasparro_list_position,
        "position_basis": out.position_basis if out.kasparro_mentioned else "not_mentioned",
        "rationale": out.rationale,
        "validation_warnings": warnings,
    }


def analyse_response(provider: Provider, *, response_id: str, question: str, body: str,
                     max_attempts: int) -> AnalysisOutcome:
    messages = build_messages(question, body)
    sha = input_hash(messages)
    attempts: list[AttemptTrace] = []
    convo = list(messages)
    last_reason = "no attempts made"
    for attempt in range(1, max_attempts + 1):
        req = CallRequest(response_id=response_id, attempt=attempt, input_sha256=sha,
                          messages=convo, schema=OUTPUT_SCHEMA)
        t0 = time.perf_counter()
        raw = None
        try:
            raw = provider.generate(req)
            labels = validate_output(raw, body)
        except ReplayMissing as e:
            attempts.append(AttemptTrace(attempt, "replay_missing", str(e), _ms(t0), None))
            return AnalysisOutcome("failed", f"replay_missing: {e}", None, attempts, sha)
        except ProviderTimeout as e:
            last_reason = f"timeout: {e}"
            attempts.append(AttemptTrace(attempt, "timeout", str(e), _ms(t0), None))
            continue
        except ProviderError as e:
            last_reason = f"provider_error: {e}"
            attempts.append(AttemptTrace(attempt, "provider_error", str(e), _ms(t0), None))
            continue
        except OutputRejected as e:
            last_reason = f"{e.kind}_output: {'; '.join(e.problems)[:500]}"
            attempts.append(AttemptTrace(attempt, e.kind, "; ".join(e.problems)[:2000], _ms(t0),
                                         (raw or "")[:MAX_RAW_OUTPUT_CHARS]))
            # Give the model the deterministic validator's feedback for the next attempt.
            convo = messages + [
                {"role": "assistant", "content": (raw or "")[:MAX_RAW_OUTPUT_CHARS]},
                {"role": "user", "content": "Your JSON was rejected by the validator:\n- "
                 + "\n- ".join(e.problems[:8])
                 + "\nReturn corrected JSON only. Quotes must be copied exactly from the ANSWER."},
            ]
            continue
        attempts.append(AttemptTrace(attempt, "ok", None, _ms(t0), raw[:MAX_RAW_OUTPUT_CHARS]))
        return AnalysisOutcome("succeeded", None, labels, attempts, sha)
    return AnalysisOutcome("failed", f"{last_reason} (after {max_attempts} attempts)", None, attempts, sha)


def _ms(t0: float) -> int:
    return int((time.perf_counter() - t0) * 1000)
