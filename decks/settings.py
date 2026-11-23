from typing import Literal

from agents import ModelSettings, OpenAIChatCompletionsModel, OpenAIResponsesModel, RunConfig
from openai import AsyncAzureOpenAI
from openai.types.shared import Reasoning
from pydantic import SecretStr
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

    def run_config(self) -> RunConfig:
        """Return a ``RunConfig`` that sends every agent call to the Azure deployment."""
        client = AsyncAzureOpenAI(
            azure_endpoint=self.endpoint,
            api_key=self.api_key.get_secret_value(),
            api_version=self.api_version,
        )
        model = (
            OpenAIResponsesModel(model=self.deployment, openai_client=client)
            if self.api == "responses"
            else OpenAIChatCompletionsModel(model=self.deployment, openai_client=client)
        )
        settings = (
            ModelSettings(reasoning=Reasoning(effort=self.reasoning_effort))
            if self.reasoning_effort is not None
            else None
        )
        return RunConfig(model=model, model_settings=settings, tracing_disabled=True)
