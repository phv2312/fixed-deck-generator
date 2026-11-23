from decks.agents.exceptions import ProjectNotFoundError
from decks.agents.repos.base import AtomicJsonStore
from decks.models.build import BuildState, ProjectInfo


class ProjectRepository:
    """Persist project metadata and build state."""

    def __init__(
        self, project_id: str, info_store: AtomicJsonStore, state_store: AtomicJsonStore
    ) -> None:
        self._project_id = project_id
        self._info = info_store
        self._state = state_store

    def create(self, name: str) -> ProjectInfo:
        """Create the project metadata and an empty state."""
        info = ProjectInfo(id=self._project_id, name=name)
        self._info.write_model(info)
        self._state.write_model(BuildState())
        return info

    def load_info(self) -> ProjectInfo:
        """Return the project metadata. Raise when the project does not exist."""
        info = self._info.read_model(ProjectInfo)
        if info is None:
            raise ProjectNotFoundError(self._project_id)
        return info

    def load_state(self) -> BuildState:
        """Return the build state. A new project has the default state."""
        return self._state.read_model(BuildState) or BuildState()

    def save_state(self, state: BuildState) -> None:
        """Write ``state``."""
        self._state.write_model(state)
