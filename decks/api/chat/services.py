import asyncio
from collections.abc import AsyncIterator

from agents import RunConfig

from decks.agents import ProjectContext, ProjectRepositories, ProjectRunner
from decks.agents.catalog import SlideCatalog
from decks.agents.exceptions import TurnInProgressError
from decks.agents.models import StreamEvent
from decks.agents.services.events import EventSink
from decks.api.chat.exceptions import ToolCallNotFoundError, ToolFieldNotFoundError
from decks.api.chat.models import ChatTranscript, FieldValue


class ChatHistoryService:
    """Read the chat of a project: its messages and the full value of a tool field."""

    def __init__(self, repositories: ProjectRepositories) -> None:
        self._repositories = repositories

    async def transcript(self, project_id: str) -> ChatTranscript:
        """Return the transcript of the chat. Raise ``ProjectNotFoundError`` for an unknown id."""
        repos = await asyncio.to_thread(self._repositories.for_project, project_id)
        items = await repos.chat.get_items()
        return ChatTranscript(items, running=repos.turn_lock.locked())

    async def field(self, project_id: str, call_id: str, key: str) -> FieldValue:
        """Return the full value of one input or output of a tool call."""
        values = (await self.transcript(project_id)).values_of(call_id)
        if values is None:
            raise ToolCallNotFoundError(project_id, call_id)
        if key not in values:
            raise ToolFieldNotFoundError(call_id, key)
        return values[key]


class ChatTurnService:
    """Start one chat turn of a project and give its events."""

    def __init__(
        self,
        repositories: ProjectRepositories,
        runner: ProjectRunner,
        catalog: SlideCatalog,
        run_config: RunConfig,
    ) -> None:
        self._repositories = repositories
        self._runner = runner
        self._catalog = catalog
        self._run_config = run_config

    async def start(self, project_id: str, message: str) -> AsyncIterator[StreamEvent]:
        """Check the project, then return the events of the turn for ``message``.

        Raise ``ProjectNotFoundError`` or ``TurnInProgressError`` before any event is sent, so
        that the caller can answer with an error status. The last event is always ``done``.
        """
        repos = await asyncio.to_thread(self._repositories.for_project, project_id)
        if repos.turn_lock.locked():
            raise TurnInProgressError(project_id)
        context = ProjectContext.create(
            repos,
            sink=EventSink(),
            slide_catalog=self._catalog,
            run_config=self._run_config,
        )
        return self._runner.run(message, context)
