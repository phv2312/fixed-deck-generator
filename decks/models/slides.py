"""Stage-0 input: per-slide-type parameters, and stage-1 output: the Deck."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Annotated, Literal

from pydantic import BaseModel, Field

from .analytics import BubbleSlide, ExhibitSlide, MekkoSlide, TwoChartsSlide
from .body import (
    FromToSlide,
    GlossarySlide,
    KeyFiguresSlide,
    PanelsSlide,
    RowsSlide,
    TableSlide,
    TerminalSlide,
)
from .decisions import (
    DecisionSlide,
    EvaluationSlide,
    ForAgainstSlide,
    OptionsSlide,
    RaciSlide,
    ScorecardSlide,
    SwotSlide,
)
from .diagram import (
    CycleSlide,
    DriverTreeSlide,
    FishboneSlide,
    FunnelSlide,
    LayersSlide,
    MatrixSlide,
    OrgSlide,
    PillarsSlide,
    ProcessSlide,
    PyramidSlide,
    SwimlanesSlide,
    VennSlide,
)
from .elements import Element, Group
from .layout import (
    AgendaSlide,
    ChapterSlide,
    ContactSlide,
    ContentSlide,
    StatementSlide,
    TitleSlide,
)
from .pictures import FigureSlide, ScreenshotSlide
from .programme import DiscussionSlide, GanttSlide, StepsSlide, TimelineSlide, TrackerSlide
from .theme import ThemeName

SlideSpec = Annotated[
    # analytics
    BubbleSlide
    | ExhibitSlide
    | MekkoSlide
    | TwoChartsSlide
    # body
    | FromToSlide
    | GlossarySlide
    | KeyFiguresSlide
    | PanelsSlide
    | RowsSlide
    | TableSlide
    | TerminalSlide
    # decisions
    | DecisionSlide
    | EvaluationSlide
    | ForAgainstSlide
    | OptionsSlide
    | RaciSlide
    | ScorecardSlide
    | SwotSlide
    # diagram
    | CycleSlide
    | DriverTreeSlide
    | FishboneSlide
    | FunnelSlide
    | LayersSlide
    | MatrixSlide
    | OrgSlide
    | PillarsSlide
    | ProcessSlide
    | PyramidSlide
    | SwimlanesSlide
    | VennSlide
    # layout
    | AgendaSlide
    | ChapterSlide
    | ContactSlide
    | ContentSlide
    | StatementSlide
    | TitleSlide
    # pictures
    | FigureSlide
    | ScreenshotSlide
    # programme
    | DiscussionSlide
    | GanttSlide
    | StepsSlide
    | TimelineSlide
    | TrackerSlide,
    Field(discriminator="type"),
]  # add more slide types here


class DeckSpec(BaseModel):
    """Input to stage 1."""

    theme: ThemeName = Field(
        default="green", description="Theme name controlling colors and fonts."
    )
    slides: list[SlideSpec] = Field(
        description=(
            "Ordered slides. Each slide has a type discriminator that matches a registered builder."
        )
    )


class Slide(BaseModel):
    id: str = ""
    family: str
    kind: str
    elements: list[Element]

    @property
    def flat(self) -> list[Element]:
        """Every element in reading order, with group children expanded."""
        return _flatten(self.elements)

    def numbered(self, index: int) -> Slide:
        """Return a copy whose elements have ids ``s{index}e{n}``."""
        counter = iter(range(1, 100_000))
        return self.model_copy(update={"elements": _numbered(self.elements, index, counter)})

    def updated(self, element_id: str, changes: dict[str, object]) -> Slide:
        """Return a copy where element ``element_id`` has ``changes`` applied."""
        return self.model_copy(update={"elements": _updated(self.elements, element_id, changes)})

    def element(self, element_id: str) -> Element | None:
        """Return the element with ``element_id``, or ``None``."""
        return next((e for e in self.flat if e.id == element_id), None)


class Deck(BaseModel):
    """Output of stage 1 (deck.json), input to every renderer."""

    width: int = 1280
    height: int = 720
    unit: Literal["px"] = "px"
    revision: int = 0
    theme: ThemeName
    palette: dict[str, str]
    font: str
    slides: list[Slide]


def _flatten(elements: list[Element]) -> list[Element]:
    flat: list[Element] = []
    for element in elements:
        flat.append(element)
        if isinstance(element, Group):
            flat.extend(_flatten(element.children))
    return flat


def _numbered(elements: list[Element], index: int, counter: Iterator[int]) -> list[Element]:
    out: list[Element] = []
    for element in elements:
        update: dict[str, object] = {"id": f"s{index}e{next(counter)}"}
        if isinstance(element, Group):
            update["children"] = _numbered(element.children, index, counter)
        out.append(element.model_copy(update=update))
    return out


def _updated(elements: list[Element], element_id: str, changes: dict[str, object]) -> list[Element]:
    out: list[Element] = []
    for element in elements:
        if element.id == element_id:
            element = element.model_copy(update=changes)
        elif isinstance(element, Group):
            element = element.model_copy(
                update={"children": _updated(element.children, element_id, changes)}
            )
        out.append(element)
    return out
