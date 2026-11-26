import asyncio
from collections.abc import Callable
from uuid import uuid4

from decks.agents.exceptions import DeckMissingError, TurnInProgressError
from decks.agents.repos import ProjectRepositories, Repos
from decks.api.projects.exceptions import SlideIndexNotFoundError
from decks.api.projects.models import ProjectSummary
from decks.render.htmldoc.models import HtmlPageStyle
from decks.render.htmldoc.services import HtmlRenderer

# A slide page that sits in an iframe: no backdrop, no gap, and it scales to the frame width.
EMBEDDED_PAGE = HtmlPageStyle(title="Slide", backdrop="transparent", gap=0, margin=0)


def new_project_id() -> str:
    """Return a new project id."""
    return uuid4().hex


class ProjectService:
    """List, create, read, and delete projects, and render one slide of a project."""

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

    async def slide_html(self, project_id: str, index: int) -> str:
        """Return the HTML page of slide ``index`` (counted from 0)."""
        return await asyncio.to_thread(self._slide_html, project_id, index)

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

    def _slide_html(self, project_id: str, index: int) -> str:
        """Render one slide of the saved deck."""
        deck = self._repositories.for_project(project_id).deck.load()
        if deck is None:
            raise DeckMissingError
        if not 0 <= index < len(deck.slides):
            raise SlideIndexNotFoundError(project_id, index)
        return HtmlRenderer(deck, EMBEDDED_PAGE).slide_document(index)
