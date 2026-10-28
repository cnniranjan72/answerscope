"""Identity configuration comes only from the server environment and must be safe."""
import pytest

from app import config


@pytest.fixture
def env(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "ROOT", tmp_path)  # ignore the developer's real .env
    for k in ("ANALYST_TOKEN", "REVIEWER_TOKEN", "ANALYST_NAME", "REVIEWER_NAME", "MODEL_PROVIDER"):
        monkeypatch.delenv(k, raising=False)
    return monkeypatch


@pytest.mark.parametrize("analyst,reviewer,msg", [
    ("", "reviewer-token-0123456789", "must be set"),
    ("short", "reviewer-token-0123456789", "must be set"),
    ("same-token-0123456789", "same-token-0123456789", "must differ"),
    ("change-me-analyst-token-0000", "reviewer-token-0123456789", "placeholder"),
])
def test_unsafe_token_configuration_refused(env, analyst, reviewer, msg):
    env.setenv("ANALYST_TOKEN", analyst)
    env.setenv("REVIEWER_TOKEN", reviewer)
    with pytest.raises(config.ConfigError, match=msg):
        config.load_settings()


def test_identities_mapped_from_environment(env):
    env.setenv("ANALYST_TOKEN", "analyst-token-0123456789")
    env.setenv("REVIEWER_TOKEN", "reviewer-token-0123456789")
    s = config.load_settings()
    assert {i.role for i in s.tokens.values()} == {"analyst", "reviewer"}
    assert "analyst-token" not in repr(s)  # tokens never appear in reprs/logs
