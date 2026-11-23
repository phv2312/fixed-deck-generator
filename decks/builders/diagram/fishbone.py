"""Fishbone slides: causes grouped around an effect."""

import math

from decks.builders.base import BaseBuilder
from decks.builders.common import MARGIN, RADIUS, TYPE, W, mid_text, title_el
from decks.models.diagram import FishboneSlide
from decks.models.elements import Element, Line, Shape


class FishboneBuilder(BaseBuilder[FishboneSlide]):
    """Render a fishbone diagram of causes leading to an effect."""

    TYPE = "fishbone"
    DESCRIPTION = (
        "Use this slide for root-cause analysis. The slide shows an effect at the head and cause "
        "categories as bones along a spine."
    )
    SPEC = FishboneSlide

    def build(self, spec: FishboneSlide) -> list[Element]:
        n = len(spec.categories)
        spine_y = 385
        x_end = 1000
        els: list[Element] = [title_el(spec.title)]
        els.append(
            Line(x1=MARGIN, y1=spine_y, x2=x_end, y2=spine_y, color="primary", width=4, arrow=True)
        )
        els.append(
            Shape(
                x=x_end,
                y=spine_y - 70,
                w=W - MARGIN - x_end,
                h=140,
                fill="primary",
                radius=RADIUS["md"],
            )
        )
        els.append(
            mid_text(
                x=x_end + 12,
                y=spine_y - 70,
                w=W - MARGIN - x_end - 24,
                h=140,
                text=spec.effect,
                font_size=TYPE["body_l"],
                bold=True,
                color="bg",
                align="center",
            )
        )
        per_side = math.ceil(n / 2)
        step = (x_end - MARGIN - 40) / per_side
        for i, category in enumerate(spec.categories):
            top = i % 2 == 0
            slot = i // 2
            bx = MARGIN + 200 + step * slot
            y_out = 175 if top else 595
            els.append(Line(x1=bx - 90, y1=y_out, x2=bx, y2=spine_y, color="primary", width=2.5))
            els.append(
                Shape(
                    x=bx - 90 - 75,
                    y=y_out - (34 if top else 0),
                    w=150,
                    h=34,
                    fill="primary",
                    radius=RADIUS["md"],
                )
            )
            els.append(
                mid_text(
                    x=bx - 90 - 75,
                    y=y_out - (34 if top else 0),
                    w=150,
                    h=34,
                    text=category.label,
                    font_size=TYPE["body"],
                    bold=True,
                    color="bg",
                    align="center",
                )
            )
            for k, cause in enumerate(category.causes):
                t = (k + 1) / (len(category.causes) + 1)
                yy = y_out + (spine_y - y_out) * t
                xx = bx - 90 + 90 * t
                els.append(Line(x1=xx - 20, y1=yy, x2=xx, y2=yy, color="muted", width=1.2))
                els.append(
                    mid_text(
                        x=xx - 24 - 190,
                        y=yy - 12,
                        w=190,
                        h=24,
                        text=cause,
                        font_size=TYPE["small"],
                        align="right",
                    )
                )
        return els
