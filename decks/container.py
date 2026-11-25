from contextlib import AsyncExitStack
from functools import cached_property
from typing import Self

from agents import Agent, ModelSettings, OpenAIChatCompletionsModel, OpenAIResponsesModel, RunConfig
from agents.memory import SessionSettings
from openai import AsyncAzureOpenAI
from openai.types.shared import Reasoning

from decks.agents.catalog import SlideCatalog
from decks.agents.context import ProjectContext
from decks.agents.repos import ProjectRepositories
from decks.agents.runner import ProjectRunner
from decks.agents.services.history import HistoryTrimmer
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
    def openai_model(self) -> OpenAIResponsesModel | OpenAIChatCompletionsModel:
        """The Azure model that every agent uses."""
        azure = self._settings.azure
        return (
            OpenAIResponsesModel(model=azure.deployment, openai_client=self.azure_client)
            if azure.api == "responses"
            else OpenAIChatCompletionsModel(model=azure.deployment, openai_client=self.azure_client)
        )

    @cached_property
    def run_config(self) -> RunConfig:
        """A ``RunConfig`` that sends every agent call to the Azure deployment.

        It limits the chat history that a turn loads, and it trims the model input.
        """
        azure = self._settings.azure
        model_settings = (
            ModelSettings(reasoning=Reasoning(effort=azure.reasoning_effort))
            if azure.reasoning_effort is not None
            else None
        )
        return RunConfig(
            model=self.openai_model,
            model_settings=model_settings,
            tracing_disabled=True,
            session_settings=SessionSettings(limit=self._settings.history_limit),
            call_model_input_filter=HistoryTrimmer(),
        )

    @cached_property
    def slide_catalog(self) -> SlideCatalog:
        """The slide catalog. The agents and the contexts share it."""
        return SlideCatalog()

    @cached_property
    def interview_agent(self) -> Agent[ProjectContext]:
        """The agent that interviews the user until the plan is approved."""
        from decks.agents.agents.interview import build_interview_agent

        return build_interview_agent(self.slide_catalog.prompt, self.openai_model)

    @cached_property
    def deck_agent(self) -> Agent[ProjectContext]:
        """The agent that builds and edits the deck."""
        from decks.agents.agents.deck import build_deck_agent

        return build_deck_agent(self.openai_model)

    @cached_property
    def repositories(self) -> ProjectRepositories:
        """The project repositories under ``projects_root``."""
        return ProjectRepositories(self._settings.projects_root)

    @cached_property
    def runner(self) -> ProjectRunner:
        """The chat-turn runner."""
        return ProjectRunner(
            self.repositories,
            self.interview_agent,
            self.deck_agent,
            run_config=self.run_config,
            max_turns=self._settings.max_turns,
        )
