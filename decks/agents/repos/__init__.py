import asyncio
from dataclasses import dataclass
from pathlib import Path

from decks.agents.exceptions import ProjectNotFoundError
from decks.agents.repos.assets import ASSET_DIR, AssetRepository
from decks.agents.repos.base import AtomicJsonStore, ModelRepository, ProjectLocks
from decks.agents.repos.chat import ChatRepository
from decks.agents.repos.project import ProjectRepository
from decks.models.plan import Plan
from decks.models.slides import Deck

PROJECT_FILE = "project.json"
STATE_FILE = "state.json"
PLAN_FILE = "plan.json"
DECK_FILE = "deck.json"
CHAT_FILE = "chat.json"


@dataclass(frozen=True)
class Repos:
    """All repositories of one project, its write lock and its chat-turn lock."""

    project_id: str
    project: ProjectRepository
    plan: ModelRepository[Plan]
    deck: ModelRepository[Deck]
    chat: ChatRepository
    assets: AssetRepository
    lock: asyncio.Lock
    turn_lock: asyncio.Lock


class ProjectRepositories:
    """Build the repository bundle of a project under ``root``."""

    def __init__(self, root: Path, locks: ProjectLocks | None = None) -> None:
        self._root = root
        self._locks = locks or ProjectLocks()

    def for_project(self, project_id: str, *, must_exist: bool = True) -> Repos:
        """Return the bundle of ``project_id``. Raise when it must exist and does not."""
        folder = self._root / project_id
        if must_exist and not (folder / PROJECT_FILE).is_file():
            raise ProjectNotFoundError(project_id)
        return Repos(
            project_id=project_id,
            project=ProjectRepository(
                project_id,
                AtomicJsonStore(folder / PROJECT_FILE),
                AtomicJsonStore(folder / STATE_FILE),
            ),
            plan=ModelRepository(Plan, AtomicJsonStore(folder / PLAN_FILE)),
            deck=ModelRepository(Deck, AtomicJsonStore(folder / DECK_FILE)),
            chat=ChatRepository(project_id, AtomicJsonStore(folder / CHAT_FILE)),
            assets=AssetRepository(folder / ASSET_DIR),
            lock=self._locks.get(project_id),
            turn_lock=self._locks.turn(project_id),
        )

    def create(self, project_id: str, name: str) -> Repos:
        """Create a new project and return its bundle."""
        repos = self.for_project(project_id, must_exist=False)
        repos.project.create(name)
        return repos


__all__ = [
    "AssetRepository",
    "AtomicJsonStore",
    "ChatRepository",
    "ModelRepository",
    "ProjectLocks",
    "ProjectRepositories",
    "ProjectRepository",
    "Repos",
]
