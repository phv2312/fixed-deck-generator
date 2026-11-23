"""Content slides: title, lead, body and optional callout box."""

from decks.builders.base import BaseBuilder
from decks.builders.common import CONTENT_W, MARGIN, RADIUS, TYPE, W, mid_text, title_el
from decks.models.elements import Element, Line, Shape, Text
from decks.models.layout import ContentSlide

from .textfit import LH, est_lines, fit


def lead_text(lead: list[str], y: float = 112) -> list[Element]:
    """Return the optional lead paragraph element below a title."""
    if not lead:
        return []
    return [
        mid_text(
            x=MARGIN,
            y=y,
            w=CONTENT_W,
            h=40,
            text=" ".join(lead),
            font_size=TYPE["lead"],
            color="muted",
        )
    ]


class ContentBuilder(BaseBuilder[ContentSlide]):
    """Render a standard content slide with bullets or a single statement."""

    TYPE = "content"
    DESCRIPTION = (
        "Use this slide for general text. It has body lines or bullets. You can add a lead "
        "paragraph and a callout box."
    )
    SPEC = ContentSlide

    def build(self, spec: ContentSlide) -> list[Element]:
        els = [title_el(spec.title), *lead_text(spec.lead or [])]
        top = 170 if spec.lead else 140
        bottom = 640
        body_w = 680 if spec.box else CONTENT_W
        hi = 24 if spec.box else 30
        if spec.small:
            hi = 18
        lines = spec.body
        if len(lines) == 1:
            fs, _ = fit(lines[0], body_w, bottom - top, hi + 4, 14)
            els.append(
                Text(
                    x=MARGIN,
                    y=top,
                    w=body_w,
                    h=bottom - top,
                    text=lines[0],
                    font_size=fs,
                    valign="top",
                )
            )
        else:
            n = len(lines)
            rh = min(96, (bottom - top) / n)
            fs = hi
            while fs > 14 and any(
                est_lines(line, body_w - 36, fs) * fs * LH > rh - 10 for line in lines
            ):
                fs -= 1
            for i, line in enumerate(lines):
                y = top + rh * i
                els.append(
                    Shape(
                        x=MARGIN + 2, y=y + rh / 2 - 5, w=10, h=10, shape="ellipse", fill="accent"
                    )
                )
                els.append(
                    mid_text(
                        x=MARGIN + 36,
                        y=y,
                        w=body_w - 36,
                        h=rh,
                        text=line,
                        font_size=fs,
                    )
                )
                if i < n - 1:
                    els.append(
                        Line(
                            x1=MARGIN,
                            y1=y + rh,
                            x2=MARGIN + body_w,
                            y2=y + rh,
                            color="grid",
                            width=1,
                        )
                    )
        if spec.box:
            bx = 800
            box_w = W - MARGIN - bx
            box_text = "\n".join(spec.box)
            els.append(
                Shape(
                    x=bx, y=top, w=box_w, h=bottom - top - 20, fill="primary", radius=RADIUS["md"]
                )
            )
            box_fs, _ = fit(box_text, box_w - 72, bottom - top - 140, 38, 20, bold=True)
            els.append(
                mid_text(
                    x=bx + 36,
                    y=top + 40,
                    w=box_w - 72,
                    h=bottom - top - 100,
                    text=box_text,
                    font_size=box_fs,
                    bold=True,
                    color="bg",
                )
            )
        return els
