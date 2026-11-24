from pathlib import Path

import pytest

from decks.container import Container
from decks.settings import Settings


@pytest.fixture
def settings(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Settings:
    """Settings with fake Azure variables and a temporary project root."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://x.openai.azure.com/")
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "secret")
    monkeypatch.setenv("AZURE_OPENAI_API_VERSION", "v1")
    monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "gpt")
    monkeypatch.delenv("AZURE_OPENAI_REASONING_EFFORT", raising=False)
    monkeypatch.setenv("DECKS_PROJECTS_ROOT", str(tmp_path / "projects"))
    return Settings()


async def test_reasoning_effort_default_is_unset(settings: Settings) -> None:
    """Without a reasoning effort the run config has no model settings."""
    async with Container(settings) as container:
        assert container.run_config.model_settings is None


async def test_reasoning_effort_reaches_run_config(
    settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The value 'none' is passed to every agent run through the run config."""
    monkeypatch.setenv("AZURE_OPENAI_REASONING_EFFORT", "none")
    async with Container(Settings()) as container:
        model_settings = container.run_config.model_settings
    assert model_settings is not None
    assert model_settings.reasoning is not None
    assert model_settings.reasoning.effort == "none"


async def test_close_closes_the_azure_client(settings: Settings) -> None:
    """The Container closes the client it created."""
    async with Container(settings) as container:
        client = container.azure_client
        assert not client.is_closed()
    assert client.is_closed()


async def test_unused_client_is_not_created(settings: Settings) -> None:
    """A Container that never used the client closes without creating it."""
    container = Container(settings)
    await container.close()
    assert "azure_client" not in vars(container)


async def test_dependencies_are_shared(settings: Settings) -> None:
    """Each property returns the same object for the life of the Container."""
    async with Container(settings) as container:
        assert container.runner is container.runner
        assert container.runner is not None
