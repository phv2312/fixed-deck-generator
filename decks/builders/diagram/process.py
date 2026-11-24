"""Process slides: a process in a few steps."""

from decks.builders.base import BaseBuilder
from decks.builders.common import bullets, icon_badge, mid_text, title_el
from decks.design import CONTENT_W, MARGIN, TYPE
from decks.models.diagram import ProcessSlide
from decks.models.elements import Element, Line, Polygon, Text

TIP = 34


class ProcessBuilder(BaseBuilder[ProcessSlide]):
    """Render a chevron-style process with steps and bullet details."""

    TYPE = "process"
    DESCRIPTION = (
        "Use this slide for a sequence of 3 to 6 process steps or project phases. Each step has a "
        "heading, an icon, an optional period and optional detail bullets. You can highlight one "
        "step, for example the current phase."
    )
    SPEC = ProcessSlide

    def build(self, spec: ProcessSlide) -> list[Element]:
        n = len(spec.steps)
        gap = 8
        cw = (CONTENT_W + TIP - gap * (n - 1)) / n
        els: list[Element] = [title_el(spec.title)]
        for i, step in enumerate(spec.steps):
            x = MARGIN + (cw - TIP + gap) * i
            hi = spec.highlight == i
            pts = [(x, 160), (x + cw - TIP, 160), (x + cw, 210), (x + cw - TIP, 260), (x, 260)]
            if i:
                pts.append((x + TIP, 210))
            els.append(
                Polygon(points=pts, fill="primary" if hi or spec.highlight is None else "light")
            )
            fg = "bg" if hi or spec.highlight is None else "primary"
            els.append(
                mid_text(
                    x=x + (TIP + 8 if i else 20),
                    y=160,
                    w=cw - TIP * 2 - 20,
                    h=70 if step.period else 100,
                    text=step.head,
                    font_size=TYPE["lead"],
                    bold=True,
                    color=fg,
                )
            )
            if step.period:
                els.append(
                    mid_text(
                        x=x + (TIP + 8 if i else 20),
                        y=224,
                        w=cw - TIP * 2 - 20,
                        h=28,
                        text=step.period,
                        font_size=TYPE["small"],
                        color=fg,
                    )
                )
            bx = x + (TIP if i else 0)
            els += icon_badge(bx, 290, 40, step.icon or str(i + 1), "primary" if hi else "accent")
            els.append(Line(x1=bx, y1=345, x2=bx + cw - TIP - 14, y2=345, color="grid", width=1.5))
            if step.items:
                els.append(
                    Text(
                        x=bx,
                        y=360,
                        w=cw - TIP - 16,
                        h=250,
                        text=bullets(step.items),
                        font_size=TYPE["body_l"],
                    )
                )
        return els
