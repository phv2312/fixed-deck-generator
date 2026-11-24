"""Cycle slides: stages arranged around a centre."""

import math

from decks.builders.base import BaseBuilder
from decks.builders.common import mid_text, title_el
from decks.design import RULE, TYPE
from decks.models.diagram import CycleSlide
from decks.models.elements import Element, Shape, Text

CX, CY, R, NODE = 640, 405, 170, 36


class CycleBuilder(BaseBuilder[CycleSlide]):
    """Render a circular cycle of stages around a centre label."""

    TYPE = "cycle"
    DESCRIPTION = (
        "Use this slide for a repeating or circular process with 3 to 6 stages. You can highlight "
        "one stage."
    )
    SPEC = CycleSlide

    def build(self, spec: CycleSlide) -> list[Element]:
        n = len(spec.items)
        els: list[Element] = [
            title_el(spec.title),
            Shape(
                x=CX - R,
                y=CY - R,
                w=2 * R,
                h=2 * R,
                shape="ellipse",
                stroke="light",
                stroke_width=8,
            ),
        ]
        els.append(Shape(x=CX - 78, y=CY - 78, w=156, h=156, shape="ellipse", fill="primary"))
        els.append(
            mid_text(
                x=CX - 66,
                y=CY - 50,
                w=132,
                h=100,
                text=spec.centre,
                font_size=TYPE["body_l"],
                bold=True,
                color="bg",
                align="center",
            )
        )
        for i, item in enumerate(spec.items):
            angle = 2 * math.pi * i / n
            px, py = CX + R * math.sin(angle), CY - R * math.cos(angle)
            hi = spec.highlight == i
            els.append(
                Shape(
                    x=px - NODE,
                    y=py - NODE,
                    w=2 * NODE,
                    h=2 * NODE,
                    shape="ellipse",
                    fill="primary" if hi else "bg",
                    stroke="light",
                    stroke_width=RULE["thick"],
                )
            )
            glyph = item.icon or str(i + 1)
            els.append(
                mid_text(
                    x=px - NODE,
                    y=py - NODE,
                    w=2 * NODE,
                    h=2 * NODE,
                    text=glyph,
                    font_size=TYPE["lead"],
                    bold=True,
                    color="bg" if hi else "primary",
                    align="center",
                )
            )
            s, c = math.sin(angle), -math.cos(angle)
            if abs(s) > 0.3:
                right = s > 0
                tx = px + NODE + 14 if right else px - NODE - 14 - 240
                align = "left" if right else "right"
                ly = py - 28
            else:
                tx, align = px - 120, "center"
                ly = py - NODE - 76 if c < 0 else py + NODE + 10
            els.append(
                mid_text(
                    x=tx,
                    y=ly,
                    w=240,
                    h=26,
                    text=item.label,
                    font_size=TYPE["body_l"],
                    bold=True,
                    color="primary",
                    align=align,
                )
            )
            if item.text:
                els.append(
                    Text(
                        x=tx,
                        y=ly + 28,
                        w=240,
                        h=50,
                        text=item.text,
                        font_size=TYPE["small"],
                        color="text",
                        align=align,
                    )
                )
        return els
