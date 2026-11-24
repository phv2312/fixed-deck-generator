"""Tracker slides: streams with status, progress and next milestone."""

from decks.builders.base import BaseBuilder
from decks.builders.common import colour, mid_text, title_el
from decks.design import CONTENT_TOP, MARGIN, RADIUS, RULE, TYPE, W
from decks.models.elements import Element, Line, Shape
from decks.models.programme import TrackerSlide


class TrackerBuilder(BaseBuilder[TrackerSlide]):
    """Render a programme tracker table with status and progress."""

    TYPE = "tracker"
    DESCRIPTION = (
        "Use this slide to track workstreams. Each row shows the owner, a traffic-light status, "
        "the progress percentage and the next milestone date."
    )
    SPEC = TrackerSlide

    def build(self, spec: TrackerSlide) -> list[Element]:
        n = len(spec.rows)
        rh = min(58, 430 / n)
        cols = [
            (MARGIN, 220, "Stream"),
            (290, 140, "Owner"),
            (440, 170, "Status"),
            (620, 200, "Progress"),
            (850, 220, "Next milestone"),
            (1085, 131, "Date"),
        ]
        els: list[Element] = [title_el(spec.title)]
        for x, w, label in cols:
            els.append(
                mid_text(
                    x=x,
                    y=CONTENT_TOP,
                    w=w,
                    h=34,
                    text=label,
                    font_size=TYPE["small"],
                    bold=True,
                    color="muted",
                )
            )
        els.append(Line(x1=MARGIN, y1=176, x2=W - MARGIN, y2=176, color="primary", width=2.5))
        for i, row in enumerate(spec.rows):
            y = 182 + rh * i
            els.append(
                mid_text(
                    x=MARGIN,
                    y=y,
                    w=220,
                    h=rh,
                    text=row.stream,
                    font_size=TYPE["body"],
                    bold=True,
                    color="primary",
                )
            )
            if row.owner:
                els.append(
                    mid_text(
                        x=290,
                        y=y,
                        w=140,
                        h=rh,
                        text=row.owner,
                        font_size=TYPE["small"],
                    )
                )
            mark = colour(row.state)
            color, glyph = mark.colour, mark.glyph
            els.append(Shape(x=440, y=y + rh / 2 - 12, w=24, h=24, shape="ellipse", fill=color))
            els.append(
                mid_text(
                    x=440,
                    y=y + rh / 2 - 12,
                    w=24,
                    h=24,
                    text=glyph,
                    font_size=TYPE["small"],
                    bold=True,
                    color="bg",
                    align="center",
                )
            )
            els.append(
                mid_text(
                    x=472,
                    y=y,
                    w=140,
                    h=rh,
                    text=row.state,
                    font_size=TYPE["small"],
                )
            )
            if row.percent is not None:
                els.append(
                    Shape(x=620, y=y + rh / 2 - 8, w=150, h=16, fill="tint", radius=RADIUS["pill"])
                )
                if row.percent > 0:
                    els.append(
                        Shape(
                            x=620,
                            y=y + rh / 2 - 8,
                            w=max(16, 150 * row.percent / 100),
                            h=16,
                            fill="primary",
                            radius=RADIUS["pill"],
                        )
                    )
                els.append(
                    mid_text(
                        x=778,
                        y=y,
                        w=60,
                        h=rh,
                        text=f"{row.percent:g} %",
                        font_size=TYPE["small"],
                        bold=True,
                    )
                )
            if row.next:
                els.append(
                    mid_text(
                        x=850,
                        y=y,
                        w=225,
                        h=rh,
                        text=row.next,
                        font_size=TYPE["small"],
                    )
                )
            if row.date:
                els.append(
                    mid_text(
                        x=1085,
                        y=y,
                        w=131,
                        h=rh,
                        text=row.date,
                        font_size=TYPE["small"],
                        bold=True,
                        color="primary",
                    )
                )
            els.append(
                Line(
                    x1=MARGIN, y1=y + rh, x2=W - MARGIN, y2=y + rh, color="grid", width=RULE["hair"]
                )
            )
        return els
