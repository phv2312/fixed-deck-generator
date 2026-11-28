import json
from dataclasses import dataclass
from typing import Annotated, Literal

from pydantic import BaseModel, Field

from decks.models.build import Phase
from decks.models.elements import Chart, Element, Image, Shape, Table, Text
from decks.models.plan import Plan, SlideDraft
from decks.models.slides import Deck, Slide


class LayoutIssue(BaseModel):
    """One layout problem found on a slide, with a suggested fix."""

    code: Literal[
        "text_overflow",
        "out_of_bounds",
        "empty_slide",
        "number_mismatch",
    ]
    severity: Literal["error", "warning"]
    slide_id: str
    element_id: str | None = None
    message: str
    suggestion: str


class CheckReport(BaseModel):
    """Result of a deck check. It reports issues; it never raises."""

    ok: bool
    issues: list[LayoutIssue]
    repairs_remaining: int


class DeckReport(BaseModel):
    """Small summary of a generation run. It holds no elements."""

    built: int
    failed: list[str]
    issues: list[LayoutIssue]
    warnings: list[str]
    revision: int


class FixResult(BaseModel):
    """Result of rebuilding one slide with instructions."""

    slide_id: str
    issues: list[LayoutIssue]
    repairs_remaining: int


class Question(BaseModel):
    """A question for the user, sent as the last step of a turn."""

    question: str
    options: list[str] | None = None
    allow_multiple: bool = False
    free_text: bool = True


class VarietyViolation(BaseModel):
    """A variety rule that the slide kinds break. ``slide_id`` is the slide to change."""

    slide_id: str
    message: str

    @property
    def line(self) -> str:
        """The violation as one line for the model or the user."""
        return f"slide {self.slide_id}: {self.message}"


class SlideRef(BaseModel):
    """Short reference to a plan slide, returned by the plan-slide tools."""

    id: str
    kind: str | None
    title: str
    plan_revision: int
    missing: list[str]
    variety: list[str]
    phase: Phase
    next_action: str

    @classmethod
    def of(
        cls,
        plan: Plan,
        draft: SlideDraft,
        phase: Phase,
        variety: list[VarietyViolation],
        next_action: str,
    ) -> "SlideRef":
        """Reference ``draft`` as a slide of ``plan`` in ``phase``, with advice and next step."""
        return cls(
            id=draft.id,
            kind=draft.kind,
            title=draft.title,
            plan_revision=plan.revision,
            missing=plan.missing,
            variety=[v.line for v in variety],
            phase=phase,
            next_action=next_action,
        )


class PlanView(BaseModel):
    """Plan summary for the model: one line per meta key and per slide."""

    revision: int
    theme: str
    meta: list[str]
    slides: list[str]
    missing: list[str]
    variety: list[str]
    approved: bool
    next_action: str

    @classmethod
    def of(cls, plan: Plan, variety: list[VarietyViolation], next_action: str) -> "PlanView":
        """Summarise ``plan`` with the variety advice and the next step."""
        return cls(
            revision=plan.revision,
            theme=plan.theme,
            meta=[f"{k}={v}" for k, v in plan.meta.items()],
            slides=[f"{s.id} [{s.kind or '?'}] {s.title} - {s.purpose}" for s in plan.slides],
            missing=plan.missing,
            variety=[v.line for v in variety],
            approved=plan.approved,
            next_action=next_action,
        )


class PlanMetaView(BaseModel):
    """Meta keys of the plan after a meta change."""

    meta: list[str]
    theme: str
    missing: list[str]
    phase: Phase
    next_action: str

    @classmethod
    def of(cls, plan: Plan, phase: Phase, next_action: str) -> "PlanMetaView":
        """Show the meta of ``plan`` in ``phase`` with the next step."""
        return cls(
            meta=[f"{k}={v}" for k, v in plan.meta.items()],
            theme=plan.theme,
            missing=plan.missing,
            phase=phase,
            next_action=next_action,
        )


class CheckIssue(BaseModel):
    """One plan problem found by final_check, with the slide to change and how to fix it."""

    slide_id: str
    fix: str


class PlanCheck(BaseModel):
    """Result of final_check: concrete issues and what to do next."""

    revision: int
    ok: bool
    issues: list[CheckIssue]
    checks_remaining: int
    next_action: str


class StylePatch(BaseModel):
    """Flat style change of one element. A field left as ``None`` stays as it is."""

    font_size: float | None = None
    bold: bool | None = None
    italic: bool | None = None
    underline: bool | None = None
    color: str | None = None
    font_family: str | None = None
    align: Literal["left", "center", "right"] | None = None
    valign: Literal["top", "middle", "bottom"] | None = None
    fill: str | None = None
    stroke: str | None = None
    opacity: float | None = None


class ElementView(BaseModel):
    """Short view of one element: id, type, text, box and style."""

    id: str
    type: str
    text: str | None = None
    bbox: tuple[float, float, float, float] | None = None
    style: dict[str, str] = Field(default_factory=dict)

    @classmethod
    def of(cls, element: Element) -> "ElementView":
        """Project ``element`` to a short view: id, type, text (80 chars), box and style."""
        data = element.model_dump(exclude={"id", "type", "text", "x", "y", "w", "h", "children"})
        box = (
            (element.x, element.y, element.w, element.h)
            if isinstance(element, Text | Shape | Image | Table | Chart)
            else None
        )
        text = element.text[:80] if isinstance(element, Text) else None
        if isinstance(element, Table):
            data.pop("rows")
            text = json.dumps(element.rows, ensure_ascii=False)  # whole, so the agent can edit it
        style = {k: str(v) for k, v in data.items() if v not in (None, "", [], {}, False)}
        return cls(id=element.id, type=element.type, text=text, bbox=box, style=style)


class SlideView(BaseModel):
    """Short view of one slide and its elements."""

    id: str
    kind: str
    elements: list[ElementView]


class ElementChange(BaseModel):
    """An element after an edit, with the issues of its slide."""

    element: ElementView
    issues: list[LayoutIssue]


class TextFitResult(BaseModel):
    """Result of a text edit, with the font fit outcome."""

    element: ElementView
    overflow: bool
    font_size: float
    suggested_font_size: float | None
    issues: list[LayoutIssue]


class _Event(BaseModel):
    """Base of the stream events. Each subclass declares its own ``type`` literal."""


class RunStarted(_Event):
    """A turn started in ``phase`` with ``agent``."""

    type: Literal["run_started"] = "run_started"
    agent: str
    phase: Phase


class Status(_Event):
    """A short progress message."""

    type: Literal["status"] = "status"
    message: str


class Token(_Event):
    """A piece of reply text."""

    type: Literal["token"] = "token"
    text: str


class ToolStarted(_Event):
    """A tool call began. Its arguments are not sent."""

    type: Literal["tool_started"] = "tool_started"
    name: str


class ToolFinished(_Event):
    """A tool call ended."""

    type: Literal["tool_finished"] = "tool_finished"
    name: str
    ok: bool = True


class QuestionEvent(_Event):
    """The agent asks the user a question. The turn ends after it."""

    type: Literal["question"] = "question"
    question: str
    options: list[str] | None = None
    allow_multiple: bool = False
    free_text: bool = True


class PlanUpdated(_Event):
    """The plan changed."""

    type: Literal["plan_updated"] = "plan_updated"
    revision: int
    slide_count: int
    missing: list[str]


class DeckProgress(_Event):
    """One slide of a generation finished."""

    type: Literal["deck_progress"] = "deck_progress"
    index: int
    total: int
    slide_id: str
    kind: str


class DeckReady(_Event):
    """A generation finished."""

    type: Literal["deck_ready"] = "deck_ready"
    built: int
    failed: list[str]
    warnings: list[str]


class ErrorEvent(_Event):
    """The turn failed. ``code`` is the error class name."""

    type: Literal["error"] = "error"
    code: str
    message: str


class Done(_Event):
    """Last event of every stream."""

    type: Literal["done"] = "done"


type StreamEvent = Annotated[
    RunStarted
    | Status
    | Token
    | ToolStarted
    | ToolFinished
    | QuestionEvent
    | PlanUpdated
    | DeckProgress
    | DeckReady
    | ErrorEvent
    | Done,
    Field(discriminator="type"),
]


@dataclass(frozen=True)
class PlanSlideChange:
    """A plan after one slide change, with the slide that changed."""

    plan: Plan
    draft: SlideDraft


@dataclass(frozen=True)
class SlideLocation:
    """A slide of the deck, with its position in the deck."""

    deck: Deck
    slide: Slide
    index: int


@dataclass(frozen=True)
class FallbackResult:
    """A plain fallback slide, or ``None``, with the warnings of the fallback."""

    slide: Slide | None
    warnings: list[str]
