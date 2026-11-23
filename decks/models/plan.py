import hashlib

from pydantic import BaseModel, Field

from decks.models.build import Phase
from decks.models.theme import DEFAULT_THEME, ThemeName

REQUIRED_META = ("audience",)


class ContentItem(BaseModel):
    """A labelled figure, such as a KPI."""

    label: str = Field(description="Item label, such as a KPI name.")
    value: str = Field(description="Item value, such as a figure or a short text.")


class ContentSeries(BaseModel):
    """One named data series of a chart."""

    name: str = Field(description="Series name.")
    values: list[float] = Field(description="One value per category.")


class ContentBlock(BaseModel):
    """Semantic content of a slide. It does not depend on one slide kind."""

    summary: str = Field(default="", description="One or two sentences of the key message.")
    points: list[str] = Field(default_factory=list, description="Bullet-style statements.")
    items: list[ContentItem] = Field(default_factory=list, description="Labelled figures or KPIs.")
    rows: list[list[str]] = Field(default_factory=list, description="Table-like data rows.")
    categories: list[str] = Field(
        default_factory=list, description="Category labels of the chart data series, in order."
    )
    series: list[ContentSeries] = Field(default_factory=list, description="Chart data series.")
    stages: list[str] = Field(default_factory=list, description="Ordered steps or phases.")
    image: str | None = Field(default=None, description="Image path or URL.")
    source: str | None = Field(default=None, description="Source note for the data.")


class SlideDraft(BaseModel):
    """One slide of the plan: purpose, title, optional kind and semantic content."""

    id: str
    kind: str | None = None
    purpose: str
    title: str
    content: ContentBlock = Field(default_factory=ContentBlock)

    @property
    def fingerprint(self) -> str:
        """Stable JSON of the fields that decide how the slide is built."""
        return self.model_dump_json(include={"kind", "title", "content"})

    @property
    def content_hash(self) -> str:
        """Short hash of ``fingerprint``. A change means the slide must be rebuilt."""
        return hashlib.sha256(self.fingerprint.encode()).hexdigest()[:16]


class SlideInput(BaseModel):
    """One slide to add to the plan: purpose, title, kind from the catalog and content."""

    purpose: str = Field(description="Why the slide exists.")
    title: str = Field(description="Slide title, a statement.")
    kind: str = Field(description="Slide kind from the catalog.")
    content: ContentBlock = Field(description="Semantic content of the slide.")


class SlideDraftPatch(BaseModel):
    """Fields of a slide draft to change. A field left as ``None`` stays as it is."""

    kind: str | None = None
    purpose: str | None = None
    title: str | None = None
    content: ContentBlock | None = None


class Plan(BaseModel):
    """Everything collected before the build: theme, meta facts and slide drafts."""

    revision: int = 0
    approved: bool = False
    theme: ThemeName = DEFAULT_THEME
    meta: dict[str, str] = Field(default_factory=dict)
    slides: list[SlideDraft] = Field(default_factory=list)

    @property
    def missing(self) -> list[str]:
        """Required keys that the plan does not have yet."""
        gaps = [key for key in REQUIRED_META if not self.meta.get(key)]
        if not self.slides:
            gaps.append("slides")
        return gaps

    def slide(self, slide_id: str) -> SlideDraft | None:
        """Return the slide draft with ``slide_id``, or ``None``."""
        return next((s for s in self.slides if s.id == slide_id), None)

    def index_of(self, slide_id: str) -> int | None:
        """Return the position of ``slide_id``, or ``None``."""
        return next((i for i, s in enumerate(self.slides) if s.id == slide_id), None)

    @property
    def next_slide_id(self) -> str:
        """Id for a new slide: ``p`` and one more than the highest number in use."""
        numbers = [int(s.id[1:]) for s in self.slides if s.id[1:].isdigit()]
        return f"p{max(numbers, default=0) + 1}"

    def phase_after_edit(self, current: Phase) -> Phase:
        """Return the phase after a plan change. A running generation keeps its phase."""
        if current == "generating":
            return "generating"
        return "interviewing" if self.missing else "review"
