from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class AzureOpenAISettings(BaseSettings):
    """Azure OpenAI connection. Read from ``AZURE_OPENAI_*`` variables or from ``.env``."""

    model_config = SettingsConfigDict(
        env_prefix="AZURE_OPENAI_", env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    endpoint: str
    api_key: SecretStr
    api_version: str
    deployment: str
    api: Literal["chat_completions", "responses"] = "responses"
    reasoning_effort: Literal["none", "minimal", "low", "medium", "high", "xhigh"] | None = None


class Settings(BaseSettings):
    """Application settings. Read from ``DECKS_*`` variables or from ``.env``."""

    model_config = SettingsConfigDict(
        env_prefix="DECKS_", env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    projects_root: Path = Path("projects")
    max_turns: int = 20
    azure: AzureOpenAISettings = Field(default_factory=AzureOpenAISettings)
