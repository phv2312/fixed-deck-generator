import asyncio
import logging
from collections.abc import AsyncIterator

from agents import Agent, RunConfig, Runner

from decks.agents.agents.deck import build_deck_agent
from decks.agents.agents.interview import build_interview_agent
from decks.agents.catalog import SlideCatalog
from decks.agents.context import ProjectContext
from decks.agents.exceptions import AgentsError, TurnInProgressError
from decks.agents.models import ErrorEvent, RunStarted, StreamEvent, Token
from decks.agents.repos import ProjectRepositories, Repos
from decks.agents.services.events import EventSink, SdkEventMapper
from decks.models.build import Phase

INTERVIEW_PHASES: frozenset[Phase] = frozenset({"draft", "interviewing", "review"})

DEFAULT_MAX_TURNS = 20  # model calls allowed in one chat turn
logger = logging.getLogger(__name__)


class ProjectRunner:
    """Run one chat turn of a project. It owns the agents; callers never build them."""

    def __init__(
        self,
        repositories: ProjectRepositories,
        *,
        model: str | None = None,
        run_config: RunConfig | None = None,
        max_turns: int = DEFAULT_MAX_TURNS,
    ) -> None:
        self._repositories = repositories
        self._catalog = SlideCatalog()
        self._interviewer = build_interview_agent(self._catalog.prompt, model)
        self._deck_agent = build_deck_agent(model)
        self._run_config = run_config or RunConfig()
        self._max_turns = max_turns

    def agent_for(self, phase: Phase) -> Agent[ProjectContext]:
        """Return the agent that owns ``phase``: the interviewer until the plan is approved."""
        return self._interviewer if phase in INTERVIEW_PHASES else self._deck_agent

    async def run(self, project_id: str, query: str) -> AsyncIterator[StreamEvent]:
        """Run ``query`` against the project and yield events, ending with ``done``.

        Errors do not raise out of the stream. They arrive as an ``error`` event.
        """
        sink = EventSink()
        task = asyncio.create_task(self._produce(project_id, query, sink))
        try:
            async for event in sink.events():
                yield event
        finally:
            if not task.done():
                task.cancel()
            await asyncio.gather(task, return_exceptions=True)

    async def _produce(self, project_id: str, query: str, sink: EventSink) -> None:
        try:
            repos = self._repositories.for_project(project_id)
            if repos.turn_lock.locked():
                raise TurnInProgressError(project_id)
            async with repos.turn_lock:
                await self._run_turn(repos, query, sink)
        except AgentsError as exc:
            await sink.emit(ErrorEvent(code=type(exc).__name__, message=str(exc)))
        except Exception:  # the stream must always end with `done`
            logger.exception("turn failed for project %s", project_id)
            await sink.emit(ErrorEvent(code="internal_error", message="Internal error."))
        finally:
            await sink.close()

    async def _run_turn(self, repos: Repos, query: str, sink: EventSink) -> None:
        context = ProjectContext.create(
            repos, sink=sink, catalog=self._catalog, run_config=self._run_config
        )
        phase = repos.project.load_state().phase
        agent = self.agent_for(phase)
        await sink.emit(RunStarted(agent=agent.name, phase=phase))
        result = Runner.run_streamed(
            agent,
            query,
            context=context,
            session=repos.chat,
            run_config=self._run_config,
            max_turns=self._max_turns,
        )
        mapper = SdkEventMapper()
        async for raw in result.stream_events():
            event = mapper.map(raw)
            if event is not None:
                await sink.emit(event)
        # A question ends the interviewer's run, so it has no reply text to stream.
        if not sink.has_emitted("token") and not sink.has_emitted("question"):
            await sink.emit(Token(text=str(result.final_output or "")))
