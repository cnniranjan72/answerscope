"""Model provider adapters.

Every provider returns the raw text the model produced; parsing and validation happen
in the analyzer, so all providers go through identical checks.

execution_mode labels: 'local_model' (Ollama on this machine), 'replay' (outputs
recorded from an earlier real run), 'stub' (deterministic test double; never evidence
of model quality). 'live' is reserved for a hosted API adapter, which is not
configured in this submission.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Protocol

import httpx


class ProviderTimeout(Exception):
    pass


class ProviderError(Exception):
    pass


class ReplayMissing(ProviderError):
    """No recorded output exists for this request; not retryable."""


@dataclass
class CallRequest:
    response_id: str
    attempt: int
    input_sha256: str
    messages: list[dict]
    schema: dict


class Provider(Protocol):
    execution_mode: str
    model: str

    def generate(self, req: CallRequest) -> str: ...


@dataclass
class OllamaProvider:
    url: str
    model: str
    timeout_s: float
    max_output_tokens: int
    execution_mode: str = "local_model"
    last_metrics: dict = field(default_factory=dict)

    def generate(self, req: CallRequest) -> str:
        payload = {
            "model": self.model,
            "stream": False,
            "think": False,
            "format": req.schema,  # Ollama structured outputs: constrain to the JSON schema
            "options": {"temperature": 0, "seed": 7, "num_ctx": 8192,
                        "num_predict": self.max_output_tokens},
            "messages": req.messages,
        }
        try:
            r = httpx.post(f"{self.url}/api/chat", json=payload, timeout=self.timeout_s)
        except httpx.TimeoutException as e:
            raise ProviderTimeout(f"ollama timed out after {self.timeout_s}s") from e
        except httpx.HTTPError as e:
            raise ProviderError(f"ollama transport error: {type(e).__name__}") from e
        if r.status_code != 200:
            raise ProviderError(f"ollama HTTP {r.status_code}: {r.text[:200]}")
        body = r.json()
        self.last_metrics = {k: body.get(k) for k in
                             ("total_duration", "prompt_eval_count", "eval_count", "done_reason")}
        return body.get("message", {}).get("content", "")


@dataclass
class ReplayProvider:
    """Serves outputs recorded from a real run, one JSON file per response.
    A recording made for different model input (prompt or answer changed) is refused."""
    directory: Path
    execution_mode: str = "replay"
    model: str = "replay"

    def _load(self, response_id: str) -> dict | None:
        path = self.directory / f"{response_id}.json"
        if not path.is_file():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def generate(self, req: CallRequest) -> str:
        rec = self._load(req.response_id)
        if rec is None:
            raise ReplayMissing(f"no recording for response {req.response_id}")
        if rec["input_sha256"] != req.input_sha256:
            raise ReplayMissing("recording was made for different model input (prompt or answer changed)")
        self.model = f"replay:{rec['model']}"
        attempts = rec["attempts"]
        if req.attempt > len(attempts):
            raise ReplayMissing(f"no recorded attempt {req.attempt}")
        a = attempts[req.attempt - 1]
        if a["outcome"] == "timeout":
            raise ProviderTimeout(a.get("error") or "recorded timeout")
        if a["outcome"] == "provider_error":
            raise ProviderError(a.get("error") or "recorded provider error")
        return a["raw_output"]


@dataclass
class StubProvider:
    """Deterministic test double. By default it answers with the rule-based baseline
    labels; `scenarios` maps response_id -> a controlled failure from
    fixtures/failure_scenarios.json (transient_timeout, permanent_timeout, empty,
    malformed) or 'ungrounded' (fabricated evidence)."""
    responder: Callable[[CallRequest], str]
    scenarios: dict[str, str] = field(default_factory=dict)
    execution_mode: str = "stub"
    model: str = "stub-baseline-v1"
    calls: int = 0

    def generate(self, req: CallRequest) -> str:
        self.calls += 1
        scenario = self.scenarios.get(req.response_id)
        if scenario == "permanent_timeout" or (scenario == "transient_timeout" and req.attempt <= 2):
            raise ProviderTimeout("stub timeout")
        if scenario == "empty":
            return ""
        if scenario == "malformed":
            return '{"kasparro_mentioned": true, "kasparro_recommended": '  # truncated JSON
        out = self.responder(req)
        if scenario == "ungrounded":
            data = json.loads(out)
            data["kasparro_mentioned"] = True
            data["mention_evidence"] = ["Kasparro is the clear market leader trusted by every Fortune 500 firm."]
            out = json.dumps(data)
        return out

