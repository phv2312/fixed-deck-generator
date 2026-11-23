"""Timeline slides: milestones along a horizontal line."""

from decks.builders.base import BaseBuilder
from decks.builders.common import CONTENT_W, MARGIN, RADIUS, TYPE, icon_badge, mid_text, title_el
from decks.models.elements import Element, Line, Shape, Text
from decks.models.programme import TimelineSlide

LINE_Y = 215
CARD_Y = 310


class TimelineBuilder(BaseBuilder[TimelineSlide]):
    """Render milestones on a timeline with a today marker."""

    TYPE = "timeline"
    DESCRIPTION = (
        "Use this slide for dated milestones in order. You can also mark the current milestone and "
        "add detail cards below the milestones."
    )
    SPEC = TimelineSlide

    def build(self, spec: TimelineSlide) -> list[Element]:
        n = len(spec.milestones)
        slot = (CONTENT_W) / n
        d = min(84, slot - 22)
        cw = min(230, slot - 14)

        def cx(i: int) -> float:
            return MARGIN + slot * (i + 0.5)

        els: list[Element] = [
            title_el(spec.title),
            Line(x1=cx(0), y1=LINE_Y, x2=cx(n - 1), y2=LINE_Y, color="primary", width=3),
        ]
        for i, milestone in enumerate(spec.milestones):
            today = spec.today
            fill = "primary" if today is None or i < today else ("ink" if i == today else "accent")
            els.append(
                Line(x1=cx(i), y1=LINE_Y + d / 2, x2=cx(i), y2=CARD_Y, color="primary", width=1.5)
            )
            els.append(
                Shape(x=cx(i) - d / 2, y=LINE_Y - d / 2, w=d, h=d, shape="ellipse", fill=fill)
            )
            els.append(
                mid_text(
                    x=cx(i) - d / 2 + 4,
                    y=LINE_Y - d / 2,
                    w=d - 8,
                    h=d,
                    text=milestone.date,
                    font_size=TYPE["small"] if d > 60 else TYPE["caption"],
                    bold=True,
                    color="bg",
                    align="center",
                )
            )
            if today == i:
                els.append(
                    Shape(
                        x=cx(i) - 34,
                        y=LINE_Y - d / 2 - 34,
                        w=68,
                        h=24,
                        fill="ink",
                        radius=RADIUS["pill"],
                    )
                )
                els.append(
                    mid_text(
                        x=cx(i) - 34,
                        y=LINE_Y - d / 2 - 34,
                        w=68,
                        h=24,
                        text="Today",
                        font_size=TYPE["caption"],
                        bold=True,
                        color="bg",
                        align="center",
                    )
                )
            els.append(
                Shape(
                    x=cx(i) - cw / 2,
                    y=CARD_Y,
                    w=cw,
                    h=190,
                    fill="tint" if today == i else None,
                    radius=RADIUS["md"],
                )
            )
            y = CARD_Y + 14
            if milestone.icon:
                els += icon_badge(cx(i) - 17, y, 34, milestone.icon)
                y += 44
            if milestone.label:
                els.append(
                    Text(
                        x=cx(i) - cw / 2 + 8,
                        y=y,
                        w=cw - 16,
                        h=48,
                        text=milestone.label,
                        font_size=TYPE["body"] if cw > 150 else TYPE["small"],
                        bold=True,
                        color="primary",
                        align="center",
                        valign="top",
                    )
                )
                y += 54
            if milestone.detail:
                els.append(
                    Text(
                        x=cx(i) - cw / 2 + 8,
                        y=y,
                        w=cw - 16,
                        h=CARD_Y + 190 - y - 8,
                        text=milestone.detail,
                        font_size=TYPE["small"],
                        align="center",
                    )
                )
        return els
