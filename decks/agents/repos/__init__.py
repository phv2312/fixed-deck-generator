import asyncio
import shutil
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from decks.agents.exceptions import ProjectNotFoundError
from decks.agents.repos.assets import ASSET_DIR, AssetRepository
from decks.agents.repos.base import AtomicJsonStore, ModelRepository, ProjectLocks
from decks.agents.repos.chat import ChatRepository
from decks.agents.repos.project import ProjectRepository
from decks.models.history import DeckHistory
from decks.models.plan import Plan
from decks.models.slides import Deck

PROJECT_FILE = "project.json"
STATE_FILE = "state.json"
PLAN_FILE = "plan.json"
DECK_FILE = "deck.json"
HISTORY_FILE = "deck_history.json"
CHAT_FILE = "chat.json"


@dataclass(frozen=True)
class Repos:
    """All repositories of one project, its write lock and its chat-turn lock."""

    project_id: str
    project: ProjectRepository
    plan: ModelRepository[Plan]
    deck: ModelRepository[Deck]
    history: ModelRepository[DeckHistory]
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
            history=ModelRepository(DeckHistory, AtomicJsonStore(folder / HISTORY_FILE)),
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

    def ids(self) -> list[str]:
        """Return the id of each project under the root, sorted."""
        if not self._root.is_dir():
            return []
        return sorted(
            folder.name for folder in self._root.iterdir() if (folder / PROJECT_FILE).is_file()
        )

    def modified_at(self, project_id: str) -> datetime:
        """Return when a file of the project changed last. Raise when the project is missing."""
        folder = self._root / project_id
        self.for_project(project_id)
        newest = max(file.stat().st_mtime for file in folder.iterdir() if file.is_file())
        return datetime.fromtimestamp(newest, tz=UTC)

    def delete(self, project_id: str) -> None:
        """Remove the folder of the project. Raise when the project is missing."""
        self.for_project(project_id)
        shutil.rmtree(self._root / project_id)


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
