import asyncio
from collections.abc import Callable
from uuid import uuid4

from decks.agents.exceptions import TurnInProgressError
from decks.agents.repos import ProjectRepositories, Repos
from decks.api.projects.models import ProjectSummary


def new_project_id() -> str:
    """Return a new project id."""
    return uuid4().hex


class ProjectService:
    """List, create, read, and delete projects."""

    def __init__(
        self,
        repositories: ProjectRepositories,
        new_id: Callable[[], str] = new_project_id,
    ) -> None:
        self._repositories = repositories
        self._new_id = new_id

    async def page(self, *, limit: int, offset: int) -> tuple[list[ProjectSummary], int]:
        """Return one page of projects, newest change first, and the total count."""
        return await asyncio.to_thread(self._page, limit, offset)

    async def create(self, name: str) -> ProjectSummary:
        """Create a project with a new id."""
        repos = await asyncio.to_thread(self._repositories.create, self._new_id(), name)
        return await asyncio.to_thread(self._summary, repos)

    async def get(self, project_id: str) -> ProjectSummary:
        """Return one project. Raise ``ProjectNotFoundError`` when it does not exist."""
        return await asyncio.to_thread(self._get, project_id)

    async def delete(self, project_id: str) -> None:
        """Delete a project. Raise ``TurnInProgressError`` while a chat turn runs."""
        repos = self._repositories.for_project(project_id)
        if repos.turn_lock.locked():
            raise TurnInProgressError(project_id)
        async with repos.lock:
            await asyncio.to_thread(self._repositories.delete, project_id)

    def _page(self, limit: int, offset: int) -> tuple[list[ProjectSummary], int]:
        """Build every summary, sort them, and cut one page."""
        summaries = [self._get(project_id) for project_id in self._repositories.ids()]
        summaries.sort(key=lambda s: (s.updated_at, s.info.id), reverse=True)
        return summaries[offset : offset + limit], len(summaries)

    def _get(self, project_id: str) -> ProjectSummary:
        """Return the summary of one project."""
        return self._summary(self._repositories.for_project(project_id))

    def _summary(self, repos: Repos) -> ProjectSummary:
        """Read the files of a project and build its summary."""
        deck = repos.deck.load()
        return ProjectSummary(
            info=repos.project.load_info(),
            phase=repos.project.load_state().phase,
            updated_at=self._repositories.modified_at(repos.project_id),
            slide_count=len(deck.slides) if deck is not None else 0,
        )
