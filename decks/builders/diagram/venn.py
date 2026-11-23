"""Venn slides: two or three overlapping circles."""

import math

from decks.builders.base import BaseBuilder
from decks.builders.common import TYPE, mid_text, title_el
from decks.models.diagram import VennSlide
from decks.models.elements import Element, Polygon, Shape, Text


def lens(c1: tuple[float, float], c2: tuple[float, float], r: float) -> list[tuple[float, float]]:
    """Return the outline of the lens shared by two circles."""
    (x1, y1), (x2, y2) = c1, c2
    d = math.hypot(x2 - x1, y2 - y1)
    alpha = math.acos(min(1, d / (2 * r)))
    theta = math.atan2(y2 - y1, x2 - x1)
    pts = []
    for k in range(25):
        a = theta - alpha + 2 * alpha * k / 24
        pts.append((x1 + r * math.cos(a), y1 + r * math.sin(a)))
    for k in range(25):
        a = theta + math.pi + alpha - 2 * alpha * k / 24
        pts.append((x2 + r * math.cos(a), y2 + r * math.sin(a)))
    return pts


class VennBuilder(BaseBuilder[VennSlide]):
    """Render a two- or three-circle Venn diagram with an overlap label."""

    TYPE = "venn"
    DESCRIPTION = (
        "Use this slide to show the overlap between two or three sets. Each circle has an item "
        "list, and the overlap has a shared label."
    )
    SPEC = VennSlide

    def build(self, spec: VennSlide) -> list[Element]:
        n = len(spec.circles)
        els: list[Element] = [title_el(spec.title)]
        if n == 2:
            r = 215
            centers = [(530, 385), (750, 385)]
        else:
            r = 175
            centers = [(570, 325), (710, 325), (640, 448)]
        for cx, cy in centers:
            els.append(
                Shape(
                    x=cx - r,
                    y=cy - r,
                    w=2 * r,
                    h=2 * r,
                    shape="ellipse",
                    fill="light",
                    opacity=0.45,
                    stroke="light",
                    stroke_width=2,
                )
            )
        mx = sum(c[0] for c in centers) / n
        my = sum(c[1] for c in centers) / n
        if n == 2:
            els.append(Polygon(points=lens(centers[0], centers[1], r), fill="primary"))
            els.append(
                mid_text(
                    x=mx - 85,
                    y=my - 60,
                    w=170,
                    h=120,
                    text=spec.overlap,
                    font_size=TYPE["body"],
                    bold=True,
                    color="bg",
                    align="center",
                )
            )
        else:
            els.append(Shape(x=mx - 62, y=my - 62, w=124, h=124, shape="ellipse", fill="primary"))
            els.append(
                mid_text(
                    x=mx - 54,
                    y=my - 54,
                    w=108,
                    h=108,
                    text=spec.overlap,
                    font_size=TYPE["small"],
                    bold=True,
                    color="bg",
                    align="center",
                )
            )
        for (cx, cy), circle in zip(centers, spec.circles, strict=False):
            if n == 2:
                tx = cx + (-1 if cx < mx else 1) * 100
                ty, tw = cy, 150
            else:
                dx, dy = cx - mx, cy - my
                tx, ty, tw = cx + dx * 0.55, cy + dy * 0.55, 190
            text = "\n".join(circle.items)
            els.append(
                mid_text(
                    x=tx - tw / 2,
                    y=ty - 62,
                    w=tw,
                    h=28,
                    text=circle.label,
                    font_size=TYPE["body_l"],
                    bold=True,
                    color="primary",
                    align="center",
                )
            )
            if text:
                els.append(
                    Text(
                        x=tx - tw / 2,
                        y=ty - 30,
                        w=tw,
                        h=90,
                        text=text,
                        font_size=TYPE["body"],
                        align="center",
                    )
                )
        return els
