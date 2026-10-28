"""Shared fixtures. Engineering tests use the synthetic mini pack and the deterministic
stub provider; they say nothing about model quality (see evaluation/ for that)."""
from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import Identity, Settings
from app.db import connect
from app.main import create_app

ROOT = Path(__file__).resolve().parents[1]
MINI_PACK = ROOT / "tests" / "fixtures" / "mini_pack"
ANALYST_TOKEN = "test-analyst-token-0123456789"
REVIEWER_TOKEN = "test-reviewer-token-0123456789"


@pytest.fixture
def settings(tmp_path) -> Settings:
    return Settings(
        db_path=tmp_path / "test.db",
        pack_dir=MINI_PACK,
        replay_dir=tmp_path / "replay",
        tokens={ANALYST_TOKEN: Identity("alice-analyst", "analyst"),
                REVIEWER_TOKEN: Identity("rita-reviewer", "reviewer")},
        provider="stub",
        ollama_url="http://127.0.0.1:9",  # never contacted by tests
        ollama_model="none",
        model_timeout_s=1,
        model_max_attempts=3,
        model_max_output_tokens=200,
        max_input_chars=20_000,
        max_responses_per_analysis=200,
    )


@pytest.fixture
def client(settings) -> TestClient:
    return TestClient(create_app(settings))


@pytest.fixture
def conn(settings, client):
    c = connect(settings.db_path)
    yield c
    c.close()


A = {"Authorization": f"Bearer {ANALYST_TOKEN}"}
R = {"Authorization": f"Bearer {REVIEWER_TOKEN}"}


@pytest.fixture
def analysed(client) -> str:
    assert client.post("/datasets/pack", headers=A).status_code == 201
    r = client.post("/analyses", headers=A, json={"provider": "stub"})
    assert r.status_code == 201, r.text
    return r.json()["analysis_id"]


@pytest.fixture
def report(client, analysed) -> dict:
    r = client.post("/reports", headers=A, json={"analysis_id": analysed})
    assert r.status_code == 201, r.text
    return r.json()
