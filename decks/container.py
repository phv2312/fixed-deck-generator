from contextlib import AsyncExitStack
from functools import cached_property
from typing import Self

from agents import ModelSettings, OpenAIChatCompletionsModel, OpenAIResponsesModel, RunConfig
from openai import AsyncAzureOpenAI
from openai.types.shared import Reasoning

from decks.agents.repos import ProjectLocks, ProjectRepositories
from decks.agents.runner import ProjectRunner
from decks.settings import Settings


class Container:
    """Create and connect the dependencies of the app. Build it only at an entry point."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._stack = AsyncExitStack()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.close()

    async def close(self) -> None:
        """Close each resource that the Container created, in reverse order."""
        await self._stack.aclose()

    @cached_property
    def azure_client(self) -> AsyncAzureOpenAI:
        """The Azure OpenAI client. The Container closes it."""
        azure = self._settings.azure
        client = AsyncAzureOpenAI(
            azure_endpoint=azure.endpoint,
            api_key=azure.api_key.get_secret_value(),
            api_version=azure.api_version,
        )
        self._stack.push_async_callback(client.close)
        return client

    @cached_property
    def run_config(self) -> RunConfig:
        """A ``RunConfig`` that sends every agent call to the Azure deployment."""
        azure = self._settings.azure
        model = (
            OpenAIResponsesModel(model=azure.deployment, openai_client=self.azure_client)
            if azure.api == "responses"
            else OpenAIChatCompletionsModel(model=azure.deployment, openai_client=self.azure_client)
        )
        model_settings = (
            ModelSettings(reasoning=Reasoning(effort=azure.reasoning_effort))
            if azure.reasoning_effort is not None
            else None
        )
        return RunConfig(model=model, model_settings=model_settings, tracing_disabled=True)

    @cached_property
    def repositories(self) -> ProjectRepositories:
        """The project repositories under ``projects_root``."""
        return ProjectRepositories(self._settings.projects_root, ProjectLocks())

    @cached_property
    def runner(self) -> ProjectRunner:
        """The chat-turn runner."""
        return ProjectRunner(
            self.repositories, run_config=self.run_config, max_turns=self._settings.max_turns
        )
