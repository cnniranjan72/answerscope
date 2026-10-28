"""Environment-based configuration.

Identities and tokens come only from server-side environment variables; nothing a
caller sends can create or change them.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _load_dotenv(path: Path) -> None:
    """Minimal .env loader (no dependency). Existing environment variables win."""
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


class ConfigError(RuntimeError):
    pass


@dataclass(frozen=True)
class Identity:
    name: str
    role: str  # "analyst" | "reviewer"


@dataclass(frozen=True)
class Settings:
    db_path: Path
    pack_dir: Path
    replay_dir: Path
    tokens: dict[str, Identity] = field(repr=False)  # token -> identity; never logged
    provider: str  # default provider for analyses: replay | stub | ollama
    ollama_url: str
    ollama_model: str
    model_timeout_s: float
    model_max_attempts: int
    model_max_output_tokens: int
    max_input_chars: int
    max_responses_per_analysis: int


def load_settings() -> Settings:
    _load_dotenv(ROOT / ".env")
    env = os.environ

    analyst_token = env.get("ANALYST_TOKEN", "")
    reviewer_token = env.get("REVIEWER_TOKEN", "")
    if len(analyst_token) < 16 or len(reviewer_token) < 16:
        raise ConfigError("ANALYST_TOKEN and REVIEWER_TOKEN must be set (>= 16 chars). See .env.example.")
    if analyst_token == reviewer_token:
        raise ConfigError("ANALYST_TOKEN and REVIEWER_TOKEN must differ.")
    analyst_name = env.get("ANALYST_NAME", "analyst")
    reviewer_name = env.get("REVIEWER_NAME", "reviewer")
    if analyst_name == reviewer_name:
        raise ConfigError("ANALYST_NAME and REVIEWER_NAME must differ.")

    provider = env.get("MODEL_PROVIDER", "replay")
    if provider not in {"replay", "stub", "ollama"}:
        raise ConfigError(f"Unsupported MODEL_PROVIDER {provider!r}; use replay, stub or ollama.")

    def _path(key: str, default: str) -> Path:
        p = Path(env.get(key, default))
        return p if p.is_absolute() else ROOT / p

    return Settings(
        db_path=_path("DATABASE_PATH", "var/answerscope.db"),
        pack_dir=_path("PACK_DIR", "assignment"),
        replay_dir=_path("REPLAY_DIR", "replay"),
        tokens={
            analyst_token: Identity(analyst_name, "analyst"),
            reviewer_token: Identity(reviewer_name, "reviewer"),
        },
        provider=provider,
        ollama_url=env.get("OLLAMA_URL", "http://localhost:11434"),
        ollama_model=env.get("OLLAMA_MODEL", "gemma4:12b"),
        model_timeout_s=float(env.get("MODEL_TIMEOUT_S", "240")),
        model_max_attempts=int(env.get("MODEL_MAX_ATTEMPTS", "3")),
        model_max_output_tokens=int(env.get("MODEL_MAX_OUTPUT_TOKENS", "1200")),
        max_input_chars=int(env.get("MAX_INPUT_CHARS", "20000")),
        max_responses_per_analysis=int(env.get("MAX_RESPONSES_PER_ANALYSIS", "200")),
    )
