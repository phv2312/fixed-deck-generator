from pathlib import Path

import pytest
from pydantic import ValidationError

from decks.settings import AzureOpenAISettings


def test_azure_settings_read_from_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Variables with the ``AZURE_OPENAI_`` prefix fill the fields; the key stays secret."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://x.openai.azure.com/")
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "secret")
    monkeypatch.setenv("AZURE_OPENAI_API_VERSION", "v1")
    monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "gpt")
    settings = AzureOpenAISettings()
    assert settings.deployment == "gpt"
    assert settings.api_key.get_secret_value() == "secret"
    assert "secret" not in repr(settings)


def test_azure_settings_missing_values(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Without the variables or a ``.env`` file, loading fails with a validation error."""
    monkeypatch.chdir(tmp_path)
    for name in ("ENDPOINT", "API_KEY", "API_VERSION", "DEPLOYMENT"):
        monkeypatch.delenv(f"AZURE_OPENAI_{name}", raising=False)
    with pytest.raises(ValidationError):
        AzureOpenAISettings()


def _set_required(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://x.openai.azure.com/")
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "secret")
    monkeypatch.setenv("AZURE_OPENAI_API_VERSION", "v1")
    monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "gpt")


def test_reasoning_effort_default_is_unset(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Without AZURE_OPENAI_REASONING_EFFORT the run config has no model settings."""
    _set_required(monkeypatch, tmp_path)
    monkeypatch.delenv("AZURE_OPENAI_REASONING_EFFORT", raising=False)
    assert AzureOpenAISettings().run_config().model_settings is None


def test_reasoning_effort_none_reaches_run_config(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """The value 'none' is passed to every agent run through the run config."""
    _set_required(monkeypatch, tmp_path)
    monkeypatch.setenv("AZURE_OPENAI_REASONING_EFFORT", "none")
    settings = AzureOpenAISettings().run_config().model_settings
    assert settings is not None
    assert settings.reasoning is not None
    assert settings.reasoning.effort == "none"


def test_reasoning_effort_rejects_unknown_value(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """A value outside the allowed list fails at load time."""
    _set_required(monkeypatch, tmp_path)
    monkeypatch.setenv("AZURE_OPENAI_REASONING_EFFORT", "loud")
    with pytest.raises(ValidationError):
        AzureOpenAISettings()
