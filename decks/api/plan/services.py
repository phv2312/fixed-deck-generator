import asyncio

from decks.agents import ProjectContext, ProjectRepositories, Repos
from decks.agents.catalog import SlideCatalog
from decks.agents.exceptions import TurnInProgressError
from decks.agents.runner import INTERVIEW_PHASES
from decks.api.chat.models import ChatTranscript
from decks.api.plan.exceptions import PlanLockedError
from decks.api.plan.models import PlanSnapshot
from decks.models.build import Phase
from decks.models.plan import Plan


class PlanService:
    """Read the plan of a project and approve it."""

    def __init__(self, repositories: ProjectRepositories, catalog: SlideCatalog) -> None:
        self._repositories = repositories
        self._catalog = catalog

    async def get(self, project_id: str) -> PlanSnapshot:
        """Return the plan. A project without a plan gives an empty plan."""
        repos = await asyncio.to_thread(self._repositories.for_project, project_id)
        return await self._snapshot(repos)

    async def approve(self, project_id: str) -> PlanSnapshot:
        """Approve the plan and return it.

        Raise ``TurnInProgressError`` while a chat turn runs, ``PlanLockedError`` after the
        interview, and ``PlanMissingError`` or ``PlanIncompleteError`` for a plan that cannot
        be approved yet.
        """
        repos = await asyncio.to_thread(self._repositories.for_project, project_id)
        if repos.turn_lock.locked():
            raise TurnInProgressError(project_id)
        phase = repos.project.load_state().phase
        if phase not in INTERVIEW_PHASES:
            raise PlanLockedError(project_id, phase)
        async with repos.lock:
            await ProjectContext.create(repos, slide_catalog=self._catalog).interview.approve()
        return await self._snapshot(repos)

    async def _snapshot(self, repos: Repos) -> PlanSnapshot:
        """Read the plan, the phase and the open question of a project."""
        plan, phase = await asyncio.to_thread(self._load, repos)
        interview = ProjectContext.create(repos, slide_catalog=self._catalog).interview
        transcript = ChatTranscript(await repos.chat.get_items())
        return PlanSnapshot(
            plan=plan,
            phase=phase,
            variety=interview.variety(plan, complete=True),
            pending_question=transcript.pending_question if phase in INTERVIEW_PHASES else None,
        )

    @staticmethod
    def _load(repos: Repos) -> tuple[Plan, Phase]:
        """Read the plan and the phase from the files."""
        return repos.plan.load() or Plan(), repos.project.load_state().phase
