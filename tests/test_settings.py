import pytest
from pydantic import ValidationError

from adk_00_hello_trench.settings import Settings

ENV_KEYS = (
    "HELLO_TRENCH_MODEL",
    "GOOGLE_GENAI_USE_ENTERPRISE",
    "GOOGLE_API_KEY",
    "GOOGLE_CLOUD_PROJECT",
)


@pytest.fixture
def clean_env(monkeypatch: pytest.MonkeyPatch) -> pytest.MonkeyPatch:
    for key in ENV_KEYS:
        monkeypatch.delenv(key, raising=False)
    return monkeypatch


def load() -> Settings:
    return Settings(_env_file=None)


def test_gemini_api_with_key_uses_default_model(clean_env: pytest.MonkeyPatch) -> None:
    clean_env.setenv("GOOGLE_API_KEY", "key")

    settings = load()

    assert settings.agent_model == "gemini-flash-latest"
    assert settings.use_enterprise is False


def test_model_is_configurable(clean_env: pytest.MonkeyPatch) -> None:
    clean_env.setenv("GOOGLE_API_KEY", "key")
    clean_env.setenv("HELLO_TRENCH_MODEL", "gemini-pro-latest")

    assert load().agent_model == "gemini-pro-latest"


def test_gemini_api_without_key_fails(clean_env: pytest.MonkeyPatch) -> None:
    with pytest.raises(ValidationError, match="GOOGLE_API_KEY"):
        load()


def test_enterprise_with_project_does_not_need_key(
    clean_env: pytest.MonkeyPatch,
) -> None:
    clean_env.setenv("GOOGLE_GENAI_USE_ENTERPRISE", "1")
    clean_env.setenv("GOOGLE_CLOUD_PROJECT", "trench")

    assert load().google_cloud_project == "trench"


def test_enterprise_without_project_fails(clean_env: pytest.MonkeyPatch) -> None:
    clean_env.setenv("GOOGLE_GENAI_USE_ENTERPRISE", "1")

    with pytest.raises(ValidationError, match="GOOGLE_CLOUD_PROJECT"):
        load()
