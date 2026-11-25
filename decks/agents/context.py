from dataclasses import dataclass
from typing import Self

from agents import RunConfig

from decks.agents.catalog import SlideCatalog
from decks.agents.repos import Repos
from decks.agents.services.checker import DeckChecker
from decks.agents.services.deck_editor import DeckEditor
from decks.agents.services.events import EventSink
from decks.agents.services.fallback import SlideFallback
from decks.agents.services.fitter import LayoutFitter
from decks.agents.services.generator import DeckGenerator
from decks.agents.services.interview import InterviewService
from decks.agents.services.variety import VarietyPolicy
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
        slide_catalog: SlideCatalog | None = None,
        run_config: RunConfig | None = None,
        visuals: VisualService | None = None,
    ) -> Self:
        """Wire the services of one project from shared collaborators. Call it once per turn."""
        sink = sink if sink is not None else EventSink()
        catalog = slide_catalog if slide_catalog is not None else SlideCatalog()
        checker = DeckChecker()

        visuals = visuals if visuals is not None else VisualService(repos.assets)
        variety = VarietyPolicy(catalog, visuals_available=visuals.available)
        return cls(
            repos=repos,
            sink=sink,
            catalog=catalog,
            checker=checker,
            interview=InterviewService(repos, sink, catalog, variety=variety),
            generator=DeckGenerator(
                repos,
                sink,
                catalog,
                checker,
                fallbacks=SlideFallback(catalog),
                fitter=LayoutFitter(),
                run_config=run_config,
                visuals=visuals,
            ),
            editor=DeckEditor(repos, checker),
            visuals=visuals,
        )
