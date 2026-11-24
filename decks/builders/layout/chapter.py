"""Chapter slides: a large section number and title."""

from decks.builders.base import BaseBuilder
from decks.builders.common import TYPE, W, background, mid_text, title_el  # noqa: F401
from decks.models.elements import Element, Line, Shape, Text
from decks.models.layout import ChapterSlide
from decks.text_metrics import TextMetrics

LM = 80


class ChapterBuilder(BaseBuilder[ChapterSlide]):
    """Render a full-bleed chapter divider with section number."""

    TYPE = "chapter"
    DESCRIPTION = (
        "Use this slide as a section divider. It shows a large chapter number and title on a "
        "primary-coloured background."
    )
    SPEC = ChapterSlide

    def build(self, spec: ChapterSlide) -> list[Element]:
        number = " ".join(f"{int(x):02d}" if x.isdigit() else x for x in spec.number)
        els = background("primary")
        els += [
            Shape(x=1000, y=560, w=280, h=160, fill="bg", opacity=0.08),
            Shape(x=1100, y=470, w=110, h=160, fill="bg", opacity=0.12),
        ]
        metrics = TextMetrics()
        number_fs = metrics.fit_font_size(
            number, 220, (W - 2 * LM, 230), 100, bold=True, step=2
        ).size
        els.append(
            mid_text(
                x=LM,
                y=110,
                w=W - 2 * LM,
                h=250,
                text=number,
                font_size=number_fs,
                bold=True,
                color="light",
            )
        )
        els.append(Line(x1=LM, y1=390, x2=LM + 120, y2=390, color="bg", width=4))
        title_fs = metrics.fit_font_size(spec.title, 60, (840, 220), 32, bold=True, snap=True).size
        els.append(
            Text(
                x=LM,
                y=420,
                w=840,
                h=220,
                text=spec.title,
                font_size=title_fs,
                bold=True,
                color="bg",
                valign="top",
            )
        )
        return els
