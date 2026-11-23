"""Data of the visual pipeline: requests, issues, results and the asset manifest."""

from typing import Literal

from pydantic import BaseModel, Field

from decks.models.plan import ContentItem
from decks.models.theme import ThemeName

type VisualKind = Literal["diagram", "mockup"]
# Pixel size of every picture. The `figure` slide draws it across the content width.
PICTURE_SIZE: tuple[int, int] = (1152, 440)


class VisualRequest(BaseModel):
    """What the interview agent asks for. It must be self-contained: no chat history exists."""

    brief: str = Field(
        description=(
            "What the picture must explain. Name the message. Add every formula, label and short "
            "explanation that the picture must show, word for word: the picture carries them."
        )
    )
    rows: list[list[str]] = Field(default_factory=list, description="Table-like data rows.")
    stages: list[str] = Field(default_factory=list, description="Ordered steps of a flow.")
    items: list[ContentItem] = Field(default_factory=list, description="Labelled values.")


class VisualIssue(BaseModel):
    """One problem found in an SVG, with a suggested fix."""

    code: str
    severity: Literal["error", "warning"]
    message: str
    suggestion: str


class VisualResult(BaseModel):
    """Result of saving a visual. On failure ``ok`` is false and ``issues`` says why."""

    ok: bool
    id: str | None = None
    path: str | None = Field(default=None, description="Relative path, such as assets/v1.png.")
    alt: str | None = Field(
        default=None, description="What the picture shows. Match it to a slide."
    )
    width: int | None = None
    height: int | None = None
    issues: list[VisualIssue] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class VisualManifest(BaseModel):
    """Metadata of one saved asset. It is the ``<id>.json`` file next to the SVG and the PNG."""

    id: str
    kind: VisualKind
    alt: str
    theme: ThemeName
    warnings: list[str] = Field(default_factory=list)


class TextBox(BaseModel):
    """Bounding box of one text element, in pixels of the rendered picture."""

    text: str
    x: float
    y: float
    w: float
    h: float


class Measurement(BaseModel):
    """What Chrome reports about a rendered SVG."""

    boxes: list[TextBox] = Field(default_factory=list)
    painted: int = Field(default=0, description="Visible shapes and texts inside the frame.")
