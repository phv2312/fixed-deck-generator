from dataclasses import dataclass

from agents import RunConfig

from decks.agents.catalog import SlideCatalog
from decks.agents.repos import Repos
from decks.agents.services.checker import DeckChecker
from decks.agents.services.deck_editor import DeckEditor
from decks.agents.services.events import EventSink
from decks.agents.services.generator import DeckGenerator
from decks.agents.services.interview import InterviewService
from decks.models.build import Phase
from decks.visuals.service import VisualService


@dataclass
class ProjectContext:
    """Repositories, services and the event sink of one project turn."""

    repos: Repos
    sink: EventSink
    catalog: SlideCatalog
    checker: DeckChecker
    interview: InterviewService
    generator: DeckGenerator
    editor: DeckEditor
    visuals: VisualService

    @property
    def phase(self) -> Phase:
        """Current phase of the project."""
        return self.repos.project.load_state().phase

    @property
    def deck_enabled(self) -> bool:
        """Whether deck work is allowed: the plan is approved and complete."""
        plan = self.repos.plan.load()
        return plan is not None and plan.approved and not plan.missing

    @classmethod
    def create(
        cls,
        repos: Repos,
        *,
        sink: EventSink | None = None,
        catalog: SlideCatalog | None = None,
        run_config: RunConfig | None = None,
        visuals: VisualService | None = None,
    ) -> "ProjectContext":
        """Wire the services of one project. Call it once per chat turn."""
        sink = sink or EventSink()
        catalog = catalog or SlideCatalog()
        checker = DeckChecker()
        visuals = visuals or VisualService(repos.assets)
        return cls(
            repos=repos,
            sink=sink,
            catalog=catalog,
            checker=checker,
            interview=InterviewService(repos, sink, catalog, visuals_available=visuals.available),
            generator=DeckGenerator(
                repos, sink, catalog, checker, run_config=run_config, visuals=visuals
            ),
            editor=DeckEditor(repos, checker),
            visuals=visuals,
        )
