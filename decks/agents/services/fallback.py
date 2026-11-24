"""Build the slide of last resort without losing the content of the plan slide."""

from pydantic import BaseModel, ValidationError

from decks.agents.catalog import FALLBACK_KIND, SlideCatalog
from decks.agents.models import FallbackResult
from decks.models.plan import SlideDraft
from decks.models.slides import Slide

PICTURE_KIND = "figure"


class SlideFallback:
    """Turn a plan slide into a plain slide that keeps its picture and every line of text."""

    def __init__(self, catalog: SlideCatalog) -> None:
        self._catalog = catalog

    def build(self, draft: SlideDraft, *, cause: str = "") -> FallbackResult:
        """Return the slide, or ``None``, and the warnings. ``cause`` says why the fill failed."""
        for kind, spec in self._candidates(draft):
            slide = self._slide(draft, kind, spec)
            if slide is not None:
                reason = f" ({cause})" if cause else ""
                warnings = [f"slide {draft.id}: fell back to a plain {kind} slide{reason}"]
                lines = self.lines(draft)
                if kind == PICTURE_KIND and lines:
                    warnings.append(
                        f"slide {draft.id}: {len(lines)} text lines are not on the slide; "
                        "the picture should carry them"
                    )
                return FallbackResult(slide=slide, warnings=warnings)
        return FallbackResult(slide=None, warnings=[f"slide {draft.id}: could not be built"])

    def lines(self, draft: SlideDraft) -> list[str]:
        """Return all the text of ``draft`` as lines: points, items, rows, stages and series."""
        content = draft.content
        lines = list(content.points)
        lines += [f"{item.label}: {item.value}" for item in content.items]
        lines += [" · ".join(row) for row in content.rows]
        lines += [f"{n}. {stage}" for n, stage in enumerate(content.stages, 1)]
        lines += [f"{s.name}: {', '.join(f'{v:g}' for v in s.values)}" for s in content.series]
        return lines

    def _candidates(self, draft: SlideDraft) -> list[tuple[str, dict[str, object]]]:
        content = draft.content
        lines = self.lines(draft)
        candidates: list[tuple[str, dict[str, object]]] = []
        if content.image and PICTURE_KIND in self._catalog:
            candidates.append(
                (
                    PICTURE_KIND,
                    {
                        "title": draft.title,
                        "image": content.image,
                        "caption": content.summary or draft.title,
                        "source": content.source,
                    },
                )
            )
        body = [content.summary, *lines] if content.summary else lines
        spec: dict[str, object] = {"title": draft.title, "body": body or [draft.purpose]}
        if content.source:
            spec["lead"] = content.source
        candidates.append((FALLBACK_KIND, spec))
        return candidates

    def _slide(self, draft: SlideDraft, kind: str, spec: dict[str, object]) -> Slide | None:
        builder = self._catalog.builder(kind)
        try:
            parsed: BaseModel = builder.SPEC.model_validate(spec)
            return Slide(
                id=draft.id,
                family=self._catalog.family_of(kind),
                kind=kind,
                elements=builder.build(parsed),
            )
        except (ValidationError, ValueError):
            return None
