"""Statement slides: one large statement, optionally with a figure."""

from decks.builders.base import BaseBuilder
from decks.builders.common import RADIUS, TYPE, H, W, background, mid_text
from decks.builders.pictures.image import pic
from decks.models.elements import Element, Line, Shape, Text
from decks.models.layout import StatementSlide

from .textfit import LH, est_lines, fit

LM = 80


class StatementBuilder(BaseBuilder[StatementSlide]):
    """Render a large statement with optional figure, label and points."""

    TYPE = "statement"
    DESCRIPTION = (
        "Use this slide to emphasise one large statement, a big number or a quotation. You can add "
        "a figure with a label, up to 3 supporting points, an author for a quotation, and a "
        "background image."
    )
    SPEC = StatementSlide

    def build(self, spec: StatementSlide) -> list[Element]:
        if spec.image:
            els = pic(spec.image, 0, 0, W, H)
            els.append(Shape(x=0, y=0, w=W, h=H, fill="ink", opacity=0.65))
            fg, sub, rule = "bg", "light", "light"
        else:
            els = background("tint")
            fg, sub, rule = "primary", "muted", "accent"
        figure = spec.figure
        n = len(spec.points)
        text_w = 640 if figure else 1040
        z0, z1 = (80, 430) if n else (80, 640)
        lead = " ".join(spec.lead) if spec.lead else None
        lead_h = 44 if lead else 0
        title_fs, line_count = fit(
            spec.title, text_w, z1 - z0 - lead_h - 20, 76 if not figure else 56, 30, bold=True
        )
        text_h = line_count * title_fs * LH
        author_h = 48 if spec.author else 0
        group_h = lead_h + text_h + author_h
        y0 = z0 + (z1 - z0 - group_h) / 2
        els.append(Shape(x=LM, y=y0 - 4, w=6, h=group_h + 8, fill=rule))
        if lead:
            els.append(
                mid_text(
                    x=LM + 28,
                    y=y0,
                    w=text_w,
                    h=36,
                    text=lead,
                    font_size=TYPE["lead"],
                    bold=True,
                    color=sub,
                )
            )
        els.append(
            Text(
                x=LM + 28,
                y=y0 + lead_h,
                w=text_w - 28,
                h=text_h + 8,
                text=spec.title,
                font_size=title_fs,
                bold=True,
                color=fg,
                valign="top",
            )
        )
        if spec.author:
            els.append(
                mid_text(
                    x=LM + 28,
                    y=y0 + lead_h + text_h + 12,
                    w=text_w - 28,
                    h=36,
                    text="— " + spec.author,
                    font_size=TYPE["lead"],
                    color=sub,
                )
            )
        if figure:
            figure_text = " ".join(figure)
            els.append(
                Line(
                    x1=760,
                    y1=z0 + 40,
                    x2=760,
                    y2=z1 - 40,
                    color=sub if spec.image else "light",
                    width=2,
                )
            )
            figure_fs = max(40, min(120, 420 / (0.62 * len(figure_text))))
            label = " ".join(spec.label) if spec.label else ""
            label_h = est_lines(label, 420, TYPE["lead"]) * TYPE["lead"] * LH + 12 if label else 0
            figure_h = figure_fs * 1.3
            group_y = z0 + (z1 - z0 - figure_h - label_h) / 2
            els.append(
                mid_text(
                    x=800,
                    y=group_y,
                    w=420,
                    h=figure_h,
                    text=figure_text,
                    font_size=figure_fs,
                    bold=True,
                    color=fg,
                )
            )
            if label:
                els.append(
                    Text(
                        x=800,
                        y=group_y + figure_h + 4,
                        w=420,
                        h=label_h,
                        text=label,
                        font_size=TYPE["lead"],
                        color="light" if spec.image else "text",
                    )
                )
        for i, point in enumerate(spec.points):
            point_w = (W - 2 * LM - 24 * (n - 1)) / n
            x = LM + (point_w + 24) * i
            els.append(Shape(x=x, y=470, w=point_w, h=130, fill="bg", radius=RADIUS["md"]))
            point_fs, _ = fit(point, point_w - 56, 100, 26, 14, bold=True)
            els.append(
                mid_text(
                    x=x + 28,
                    y=470,
                    w=point_w - 56,
                    h=130,
                    text=point,
                    font_size=point_fs,
                    bold=True,
                )
            )
        return els
