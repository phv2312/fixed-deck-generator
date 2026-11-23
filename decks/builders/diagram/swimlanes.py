"""Swimlane slides: steps placed in lanes and columns with links."""

from decks.builders.base import BaseBuilder
from decks.builders.common import CONTENT_W, MARGIN, RADIUS, TYPE, W, mid_text, title_el
from decks.models.diagram import SwimlanesSlide
from decks.models.elements import Element, Line, Shape


class SwimlanesBuilder(BaseBuilder[SwimlanesSlide]):
    """Render a swimlane diagram of steps and links."""

    TYPE = "swimlanes"
    DESCRIPTION = (
        "Use this slide for cross-functional processes with lanes and numbered columns. The slide "
        "shows step boxes and labelled flow links."
    )
    SPEC = SwimlanesSlide

    def build(self, spec: SwimlanesSlide) -> list[Element]:
        lane_count = len(spec.lanes)
        cols = max(step.col for step in spec.steps) + 1
        lab_w = 150
        lh = min(130, 470 / lane_count)
        top = 140
        cw = (CONTENT_W - lab_w) / cols
        bw, bh = cw - 28, min(60, lh - 30)
        els: list[Element] = [title_el(spec.title)]
        for i, name in enumerate(spec.lanes):
            y = top + lh * i
            els.append(
                Line(x1=MARGIN, y1=y + lh - 2, x2=W - MARGIN, y2=y + lh - 2, color="grid", width=1)
            )
            els.append(
                mid_text(
                    x=MARGIN,
                    y=y,
                    w=lab_w - 16,
                    h=lh - 4,
                    text=name,
                    font_size=TYPE["body"],
                    bold=True,
                    color="primary",
                )
            )
        boxes: dict[int, tuple[float, float, float, float]] = {}
        for k, step in enumerate(spec.steps):
            li = spec.lanes.index(step.lane)
            x = MARGIN + lab_w + cw * step.col + 14
            y = top + lh * li + (lh - 4 - bh) / 2
            boxes[k] = (x, y, bw, bh)
            els.append(
                Shape(
                    x=x,
                    y=y,
                    w=bw,
                    h=bh,
                    fill="bg",
                    stroke="primary",
                    stroke_width=2,
                    radius=RADIUS["md"],
                )
            )
            els.append(
                mid_text(
                    x=x + 6,
                    y=y,
                    w=bw - 12,
                    h=bh,
                    text=step.label,
                    font_size=TYPE["small"],
                    bold=True,
                    color="primary",
                    align="center",
                )
            )
        for link in spec.links:
            ax, ay, aw, ah = boxes[link.from_]
            bx, by, bw2, bh2 = boxes[link.to]
            if abs(ay - by) < 1:
                els.append(
                    Line(
                        x1=ax + aw,
                        y1=ay + ah / 2,
                        x2=bx,
                        y2=by + bh2 / 2,
                        color="primary",
                        width=2,
                        arrow=True,
                    )
                )
            elif abs(ax - bx) < 1:
                sy = ay + ah if by > ay else ay
                ey = by if by > ay else by + bh2
                els.append(
                    Line(
                        x1=ax + aw / 2,
                        y1=sy,
                        x2=bx + bw2 / 2,
                        y2=ey,
                        color="primary",
                        width=2,
                        arrow=True,
                    )
                )
            else:
                mx = ax + aw + 14 if bx > ax else ax - 14
                els.append(
                    Line(
                        x1=ax + aw if bx > ax else ax,
                        y1=ay + ah / 2,
                        x2=mx,
                        y2=ay + ah / 2,
                        color="primary",
                        width=2,
                    )
                )
                els.append(
                    Line(x1=mx, y1=ay + ah / 2, x2=mx, y2=by + bh2 / 2, color="primary", width=2)
                )
                els.append(
                    Line(
                        x1=mx,
                        y1=by + bh2 / 2,
                        x2=bx if bx > ax else bx + bw2,
                        y2=by + bh2 / 2,
                        color="primary",
                        width=2,
                        arrow=True,
                    )
                )
        return els
