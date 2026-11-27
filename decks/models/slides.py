"""Stage-0 input: per-slide-type parameters, and stage-1 output: the Deck."""

from collections.abc import Callable, Iterator
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
from .elements import Element, Group, Line, Polygon
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


type ZMove = Literal["forward", "backward", "front", "back"]


class Slide(BaseModel):
    id: str = ""
    family: str
    kind: str
    elements: list[Element]

    @property
    def flat(self) -> list[Element]:
        """Every element in reading order, with group children expanded."""
        return self._flatten(self.elements)

    def numbered(self, index: int) -> "Slide":
        """Return a copy whose elements have ids ``s{index}e{n}``."""
        counter = iter(range(1, 100_000))
        return self.model_copy(update={"elements": self._numbered(self.elements, index, counter)})

    def updated(self, element_id: str, changes: dict[str, object]) -> "Slide":
        """Return a copy where element ``element_id`` has ``changes`` applied."""
        return self.model_copy(
            update={"elements": self._updated(self.elements, element_id, changes)}
        )

    @staticmethod
    def _flatten(elements: list[Element]) -> list[Element]:
        flat: list[Element] = []
        for element in elements:
            flat.append(element)
            if isinstance(element, Group):
                flat.extend(Slide._flatten(element.children))
        return flat

    @staticmethod
    def _numbered(elements: list[Element], index: int, counter: Iterator[int]) -> list[Element]:
        out: list[Element] = []
        for element in elements:
            update: dict[str, object] = {"id": f"s{index}e{next(counter)}"}
            if isinstance(element, Group):
                update["children"] = Slide._numbered(element.children, index, counter)
            out.append(element.model_copy(update=update))
        return out

    @staticmethod
    def _updated(
        elements: list[Element], element_id: str, changes: dict[str, object]
    ) -> list[Element]:
        out: list[Element] = []
        for element in elements:
            if element.id == element_id:
                element = element.model_copy(update=changes)
            elif isinstance(element, Group):
                element = element.model_copy(
                    update={"children": Slide._updated(element.children, element_id, changes)}
                )
            out.append(element)
        return out

    def element(self, element_id: str) -> Element | None:
        """Return the element with ``element_id``, or ``None``."""
        return next((e for e in self.flat if e.id == element_id), None)

    def patched(self, element_id: str, changes: dict[str, object]) -> "Slide":
        """Return a copy where element ``element_id`` has ``changes`` applied and validated.

        Raises:
            KeyError: If the slide has no such element.
            pydantic.ValidationError: If the changed element is not valid.
        """
        element = self.element(element_id)
        if element is None:
            raise KeyError(element_id)
        changed = type(element).model_validate({**element.model_dump(), **changes})
        return self._replaced(element_id, lambda _: changed)

    def appended(self, element: Element) -> "Slide":
        """Return a copy with ``element`` on top of the others."""
        return self.model_copy(update={"elements": [*self.elements, element]})

    def without(self, element_id: str) -> "Slide":
        """Return a copy without element ``element_id``, also when it sits in a group."""
        return self.model_copy(update={"elements": self._without(self.elements, element_id)})

    def reordered(self, element_id: str, move: ZMove) -> "Slide":
        """Return a copy where the top-level element moves in the stacking order.

        Raises:
            KeyError: If ``element_id`` is not a top-level element.
        """
        elements = list(self.elements)
        at = next((i for i, e in enumerate(elements) if e.id == element_id), None)
        if at is None:
            raise KeyError(element_id)
        target = {
            "forward": min(at + 1, len(elements) - 1),
            "backward": max(at - 1, 0),
            "front": len(elements) - 1,
            "back": 0,
        }[move]
        elements.insert(target, elements.pop(at))
        return self.model_copy(update={"elements": elements})

    def duplicated(self, element_id: str, new_id: str, offset: float = 16) -> "Slide":
        """Return a copy with a shifted copy of a top-level element above the original.

        Raises:
            KeyError: If ``element_id`` is not a top-level element.
        """
        elements = list(self.elements)
        at = next((i for i, e in enumerate(elements) if e.id == element_id), None)
        if at is None:
            raise KeyError(element_id)
        elements.insert(at + 1, self._shifted(elements[at], new_id, offset))
        return self.model_copy(update={"elements": elements})

    def _replaced(self, element_id: str, change: Callable[[Element], Element]) -> "Slide":
        return self.model_copy(update={"elements": self._mapped(self.elements, element_id, change)})

    @staticmethod
    def _mapped(
        elements: list[Element], element_id: str, change: Callable[[Element], Element]
    ) -> list[Element]:
        out: list[Element] = []
        for element in elements:
            if element.id == element_id:
                element = change(element)
            elif isinstance(element, Group):
                children = Slide._mapped(element.children, element_id, change)
                element = element.model_copy(update={"children": children})
            out.append(element)
        return out

    @staticmethod
    def _without(elements: list[Element], element_id: str) -> list[Element]:
        out: list[Element] = []
        for element in elements:
            if element.id == element_id:
                continue
            if isinstance(element, Group):
                children = Slide._without(element.children, element_id)
                element = element.model_copy(update={"children": children})
            out.append(element)
        return out

    @staticmethod
    def _shifted(element: Element, new_id: str, offset: float) -> Element:
        match element:
            case Line():
                moved: dict[str, object] = {
                    "x1": element.x1 + offset,
                    "y1": element.y1 + offset,
                    "x2": element.x2 + offset,
                    "y2": element.y2 + offset,
                }
            case Polygon():
                moved = {"points": [(x + offset, y + offset) for x, y in element.points]}
            case Group():
                raise KeyError(element.id)
            case _:
                moved = {"x": element.x + offset, "y": element.y + offset}
        return element.model_copy(update={"id": new_id, **moved})


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
