import re

from decks.agents.models import LayoutIssue
from decks.models.elements import BULLET, Chart, Image, Line, Polygon, Shape, Table, Text
from decks.models.plan import Plan, SlideDraft
from decks.models.slides import Deck, Slide
from decks.table_layout import TableLayout
from decks.text_metrics import TextMetrics

OVERFLOW_TOLERANCE = 1.02  # the height estimate is a heuristic: allow a little slack
NUMBER = re.compile(r"\d+(?:[.,]\d+)*")


class DeckChecker:
    """Check slides and return issues, never raise. Four checks: empty, bounds, overflow, numbers.

    Only the text overflow and the number check read the plan. ``error`` issues make the generator
    fill the slide again; ``warning`` issues only go in the report.
    """

    def __init__(self, metrics: TextMetrics | None = None) -> None:
        self._metrics = metrics or TextMetrics()
        self._tables = TableLayout(self._metrics)

    def check_slide(
        self, slide: Slide, draft: SlideDraft | None, *, width: int = 1280, height: int = 720
    ) -> list[LayoutIssue]:
        """Return the issues of ``slide``. ``draft`` enables the number check."""
        sid = slide.id or slide.kind
        if not slide.flat:
            return [
                LayoutIssue(
                    code="empty_slide",
                    severity="error",
                    slide_id=sid,
                    message="slide has no element",
                    suggestion="add content to the plan slide and rebuild it",
                )
            ]
        return [
            *self._bounds(sid, slide, width, height),
            *self._overflow(sid, slide),
            *self._numbers(sid, slide, draft),
        ]

    def check_deck(self, deck: Deck, plan: Plan) -> list[LayoutIssue]:
        """Return the issues of every slide of ``deck``."""
        issues: list[LayoutIssue] = []
        for slide in deck.slides:
            issues += self.check_slide(
                slide, plan.slide(slide.id), width=deck.width, height=deck.height
            )
        return issues

    def _bounds(self, sid: str, slide: Slide, width: int, height: int) -> list[LayoutIssue]:
        issues = []
        for element in slide.flat:
            box = self._box(element)
            if box is None:
                continue
            x0, y0, x1, y1 = box
            if x0 < -1 or y0 < -1 or x1 > width + 1 or y1 > height + 1:
                issues.append(
                    LayoutIssue(
                        code="out_of_bounds",
                        severity="error",
                        slide_id=sid,
                        element_id=element.id,
                        message="element leaves the slide",
                        suggestion="move or resize the element inside the slide",
                    )
                )
        return issues

    def _box(self, element: object) -> tuple[float, float, float, float] | None:
        """Return ``(x0, y0, x1, y1)`` of an element that has a position, else ``None``."""
        if isinstance(element, Line):
            xs, ys = [element.x1, element.x2], [element.y1, element.y2]
        elif isinstance(element, Polygon):
            xs, ys = [p[0] for p in element.points], [p[1] for p in element.points]
        elif isinstance(element, Text | Shape | Image | Table | Chart):
            xs, ys = [element.x, element.x + element.w], [element.y, element.y + element.h]
        else:
            return None
        return (min(xs), min(ys), max(xs), max(ys)) if xs else None

    def _overflow(self, sid: str, slide: Slide) -> list[LayoutIssue]:
        issues = []
        for element in slide.flat:
            if isinstance(element, Table):
                issues += self._table_overflow(sid, element)
            if not isinstance(element, Text):
                continue
            indent = element.font_size if BULLET in element.text else 0  # hanging bullet indent
            need = self._metrics.height(
                element.text, element.font_size, element.w - indent, bold=element.bold
            )
            if need <= element.h * OVERFLOW_TOLERANCE:
                continue
            issues.append(
                LayoutIssue(
                    code="text_overflow",
                    severity="error",
                    slide_id=sid,
                    element_id=element.id,
                    message=f"text needs {need:.0f}px of height",
                    suggestion="shorten the text",
                )
            )
        return issues

    def _table_overflow(self, sid: str, table: Table) -> list[LayoutIssue]:
        return [
            LayoutIssue(
                code="text_overflow",
                severity="error",
                slide_id=sid,
                element_id=table.id,
                message=f"table cell {cell.row},{cell.col} needs {cell.need:.0f}px of height",
                suggestion="shorten the cell text or remove a row",
            )
            for cell in self._tables.overflow(table)
        ]

    def _numbers(self, sid: str, slide: Slide, draft: SlideDraft | None) -> list[LayoutIssue]:
        if draft is None:
            return []
        known = {self._normal(n) for n in NUMBER.findall(draft.fingerprint)}
        issues = []
        for element in slide.flat:
            if isinstance(element, Table):
                text = "\n".join(cell for row in element.rows for cell in row)
            elif isinstance(element, Text):
                text = element.text
            else:
                continue
            for found in NUMBER.findall(text):
                number = self._normal(found)
                if len(number) < 2 or number in known:
                    continue
                issues.append(
                    LayoutIssue(
                        code="number_mismatch",
                        severity="warning",
                        slide_id=sid,
                        element_id=element.id,
                        message=f"{found} is not in the plan",
                        suggestion="use only figures that the plan content contains",
                    )
                )
        return issues

    def _normal(self, number: str) -> str:
        """Drop thousands commas and a trailing ``.0``, so ``1,000`` equals ``1000``."""
        plain = number.replace(",", "")
        return plain.rstrip("0").rstrip(".") if "." in plain else plain
