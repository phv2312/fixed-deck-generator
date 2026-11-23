"""Terminal slides: a mocked terminal with commands and output."""

from decks.builders.base import BaseBuilder
from decks.builders.common import (
    AMBER,
    CONTENT_W,
    GREEN,
    GREY,
    MARGIN,
    RADIUS,
    RED,
    TYPE,
    mid_text,
    title_el,
)
from decks.models.body import TerminalSlide
from decks.models.elements import Element, Line, Shape


class TerminalBuilder(BaseBuilder[TerminalSlide]):
    """Render a terminal window with commands, comments and output."""

    TYPE = "terminal"
    DESCRIPTION = (
        "Use this slide to show commands, comments and output in a terminal window. An example is "
        "an installation or CLI walkthrough."
    )
    SPEC = TerminalSlide

    def build(self, spec: TerminalSlide) -> list[Element]:
        els: list[Element] = [title_el(spec.title)]
        x, y, w, h = MARGIN, 140, CONTENT_W, 480
        els.append(Shape(x=x, y=y, w=w, h=h, fill="ink", radius=RADIUS["md"]))
        for k, color in enumerate((RED, AMBER, GREEN)):
            els.append(Shape(x=x + 18 + 24 * k, y=y + 14, w=14, h=14, shape="ellipse", fill=color))
        els.append(Line(x1=x, y1=y + 42, x2=x + w, y2=y + 42, color="muted", width=0.5))
        lh = min(32, 410 / len(spec.lines))
        for i, line in enumerate(spec.lines):
            ty = y + 54 + lh * i
            if line.kind == "command":
                els.append(
                    mid_text(
                        x=x + 24,
                        y=ty,
                        w=24,
                        h=lh,
                        text="$",
                        font_size=TYPE["body_l"],
                        bold=True,
                        color="accent",
                        mono=True,
                    )
                )
                els.append(
                    mid_text(
                        x=x + 52,
                        y=ty,
                        w=w - 76,
                        h=lh,
                        text=line.text,
                        font_size=TYPE["body_l"],
                        bold=True,
                        color="bg",
                        mono=True,
                    )
                )
            elif line.kind == "comment":
                els.append(
                    mid_text(
                        x=x + 24,
                        y=ty,
                        w=w - 48,
                        h=lh,
                        text=f"# {line.text}",
                        font_size=TYPE["body_l"],
                        color=GREY,
                        mono=True,
                    )
                )
            else:
                els.append(
                    mid_text(
                        x=x + 24,
                        y=ty,
                        w=w - 48,
                        h=lh,
                        text=line.text,
                        font_size=TYPE["body_l"],
                        color="light",
                        mono=True,
                    )
                )
        return els
