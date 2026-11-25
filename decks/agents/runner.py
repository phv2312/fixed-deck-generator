import asyncio
import logging
from collections.abc import AsyncIterator

from agents import Agent, RunConfig, Runner

from decks.agents.context import ProjectContext
from decks.agents.exceptions import AgentsError, TurnInProgressError
from decks.agents.models import ErrorEvent, RunStarted, StreamEvent, Token
from decks.agents.repos import ProjectRepositories
from decks.agents.services.events import SdkEventMapper
from decks.models.build import Phase

INTERVIEW_PHASES: frozenset[Phase] = frozenset({"draft", "interviewing", "review"})

DEFAULT_MAX_TURNS = 20  # model calls allowed in one chat turn
logger = logging.getLogger(__name__)


class ProjectRunner:
    """Run one chat turn of a project. It owns the agents; callers never build them."""

    def __init__(
        self,
        repositories: ProjectRepositories,
        interviewer: Agent[ProjectContext],
        deck_agent: Agent[ProjectContext],
        *,
        run_config: RunConfig | None = None,
        max_turns: int = DEFAULT_MAX_TURNS,
    ) -> None:
        self._repositories = repositories
        self._interviewer = interviewer
        self._deck_agent = deck_agent
        self._run_config = run_config or RunConfig()
        self._max_turns = max_turns

    def agent_for(self, phase: Phase) -> Agent[ProjectContext]:
        """Return the agent that owns ``phase``: the interviewer until the plan is approved."""
        return self._interviewer if phase in INTERVIEW_PHASES else self._deck_agent

    async def run(self, query: str, context: ProjectContext) -> AsyncIterator[StreamEvent]:
        """Run ``query`` in ``context`` and yield events, ending with ``done``.

        Errors do not raise out of the stream. They arrive as an ``error`` event.
        """
        task = asyncio.create_task(self._produce(query, context))
        try:
            async for event in context.sink.events():
                yield event
        finally:
            if not task.done():
                task.cancel()
            await asyncio.gather(task, return_exceptions=True)

    async def _produce(self, query: str, context: ProjectContext) -> None:
        try:
            if context.repos.turn_lock.locked():
                raise TurnInProgressError(context.repos.project_id)
            async with context.repos.turn_lock:
                await self._run_turn(query, context)
        except AgentsError as exc:
            await context.sink.emit(ErrorEvent(code=type(exc).__name__, message=str(exc)))
        except Exception:  # the stream must always end with `done`
            logger.exception("turn failed for project %s", context.repos.project_id)
            await context.sink.emit(ErrorEvent(code="internal_error", message="Internal error."))
        finally:
            await context.sink.close()

    async def _run_turn(self, query: str, context: ProjectContext) -> None:
        phase = context.repos.project.load_state().phase
        agent = self.agent_for(phase)
        await context.sink.emit(RunStarted(agent=agent.name, phase=phase))
        result = Runner.run_streamed(
            agent,
            query,
            context=context,
            session=context.repos.chat,
            run_config=self._run_config,
            max_turns=self._max_turns,
        )
        mapper = SdkEventMapper()
        async for raw in result.stream_events():
            event = mapper.map(raw)
            if event is not None:
                await context.sink.emit(event)
        # A question ends the interviewer's run, so it has no reply text to stream.
        if not context.sink.has_emitted("token") and not context.sink.has_emitted("question"):
            await context.sink.emit(Token(text=str(result.final_output or "")))
