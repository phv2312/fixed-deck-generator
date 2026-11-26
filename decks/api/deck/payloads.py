from typing import Annotated, Any, Literal, Self

from fastapi import Path
from pydantic import BaseModel, ConfigDict, Field

from decks.agents.models import LayoutIssue
from decks.api.deck.models import DeckInfo, EditResult, ElementInfo, NewKind, SlideInfo
from decks.models.slides import ZMove

ElementId = Annotated[
    str,
    Path(
        pattern=r"^[A-Za-z0-9_-]{1,64}$",
        description="Element id, as the deck response gives it.",
        examples=["s3e2"],
    ),
]
BaseRevision = Field(
    default=None,
    description=(
        "The deck revision that the client saw. The edit fails with `StaleDeckRevisionError` "
        "when the saved deck is newer. Leave it out to skip the check."
    ),
    examples=[7],
)


class ElementResponse(BaseModel):
    """One element: its box for an overlay, its fields, and the fields that an edit may change."""

    id: str = Field(description="Element id. The rendered HTML has it in `data-element-id`.")
    type: Literal["text", "shape", "image", "table", "chart", "polygon", "line", "group"] = Field(
        description="Element type."
    )
    parent_id: str | None = Field(description="Id of the group that holds it, or null.")
    z: int = Field(description="Position in the render order of the slide. Higher is on top.")
    x: float = Field(
        description="Left edge in canvas units. For a line, polygon, or group: the box."
    )
    y: float = Field(description="Top edge in canvas units.")
    w: float = Field(description="Width in canvas units.")
    h: float = Field(description="Height in canvas units.")
    props: dict[str, Any] = Field(
        description="The type-specific fields, such as `text`, `font_size`, `fill` or `rows`."
    )
    editable: list[str] = Field(description="Names of the fields that an edit may change.")

    @classmethod
    def from_info(cls, info: ElementInfo) -> Self:
        """Build the response from a domain element."""
        x, y, w, h = info.box
        return cls(
            id=info.id,
            type=info.type,  # ty: ignore[invalid-argument-type]
            parent_id=info.parent_id,
            z=info.z,
            x=x,
            y=y,
            w=w,
            h=h,
            props=info.props,
            editable=info.editable,
        )


class SlideResponse(BaseModel):
    """One slide with its elements in render order."""

    index: int = Field(description="Position of the slide, counted from 0.")
    id: str = Field(description="Slide id. It is the id of the plan slide.")
    kind: str = Field(description="Slide kind.")
    title: str | None = Field(description="Title of the plan slide, or null without a plan.")
    elements: list[ElementResponse] = Field(description="Elements, group children after the group.")

    @classmethod
    def from_info(cls, info: SlideInfo) -> Self:
        """Build the response from a domain slide."""
        return cls(
            index=info.index,
            id=info.id,
            kind=info.kind,
            title=info.title,
            elements=[ElementResponse.from_info(e) for e in info.elements],
        )


class DeckResponse(BaseModel):
    """The built deck for the editor."""

    revision: int = Field(description="Deck revision. It grows with each edit, undo and redo.")
    width: int = Field(description="Canvas width in canvas units.")
    height: int = Field(description="Canvas height in canvas units.")
    slides: list[SlideResponse] = Field(description="The slides, in order.")
    can_undo: bool = Field(description="Whether an undo is possible.")
    can_redo: bool = Field(description="Whether a redo is possible.")

    @classmethod
    def from_info(cls, info: DeckInfo) -> Self:
        """Build the response from a domain deck."""
        return cls(
            revision=info.revision,
            width=info.width,
            height=info.height,
            slides=[SlideResponse.from_info(s) for s in info.slides],
            can_undo=info.can_undo,
            can_redo=info.can_redo,
        )


class IssueResponse(BaseModel):
    """One layout problem on the edited slide."""

    code: str = Field(description="Kind of problem, such as `text_overflow` or `out_of_bounds`.")
    severity: Literal["error", "warning"] = Field(description="How serious it is.")
    element_id: str | None = Field(description="The element that has the problem, if any.")
    message: str = Field(description="English text for a developer.")
    suggestion: str = Field(description="English text for a developer.")

    @classmethod
    def from_issue(cls, issue: LayoutIssue) -> Self:
        """Build the response from a domain issue."""
        return cls(
            code=issue.code,
            severity=issue.severity,
            element_id=issue.element_id,
            message=issue.message,
            suggestion=issue.suggestion,
        )


class EditResponse(BaseModel):
    """The result of an edit, an undo, or a redo."""

    revision: int = Field(description="The new deck revision.")
    element: ElementResponse | None = Field(
        description="The element after the edit. Null after a delete, an undo, or a redo."
    )
    issues: list[IssueResponse] = Field(description="Layout problems on the edited slide.")
    can_undo: bool = Field(description="Whether an undo is possible.")
    can_redo: bool = Field(description="Whether a redo is possible.")

    @classmethod
    def from_result(cls, result: EditResult) -> Self:
        """Build the response from a domain result."""
        return cls(
            revision=result.revision,
            element=ElementResponse.from_info(result.element) if result.element else None,
            issues=[IssueResponse.from_issue(i) for i in result.issues],
            can_undo=result.can_undo,
            can_redo=result.can_redo,
        )


class ElementUpdate(BaseModel):
    """Request body to change fields of one element."""

    model_config = ConfigDict(extra="forbid")

    base_revision: int | None = BaseRevision
    changes: dict[str, Any] = Field(
        description=(
            "Fields to change. Each name must be in the `editable` list of the element. "
            "Use `x`, `y`, `w`, `h` to move and resize a text, shape, image, table or chart."
        ),
        examples=[{"x": 120, "y": 80, "font_size": 28, "bold": True}],
    )


class ElementCreate(BaseModel):
    """Request body to add an element to a slide."""

    model_config = ConfigDict(extra="forbid")

    base_revision: int | None = BaseRevision
    kind: NewKind = Field(description="Type of the new element.")
    props: dict[str, Any] = Field(
        default_factory=dict,
        description="Fields that replace the defaults. An image needs `src`.",
        examples=[{"text": "Hello", "x": 100, "y": 200}],
    )


class ElementDuplicate(BaseModel):
    """Request body to copy an element."""

    model_config = ConfigDict(extra="forbid")

    base_revision: int | None = BaseRevision


class ElementOrder(BaseModel):
    """Request body to change the stacking order of an element."""

    model_config = ConfigDict(extra="forbid")

    base_revision: int | None = BaseRevision
    move: ZMove = Field(description="One step up or down, or to the top or the bottom.")
