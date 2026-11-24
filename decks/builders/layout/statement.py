"""Statement slides: one large statement, optionally with a figure."""

from decks.builders.base import BaseBuilder
from decks.builders.common import background, mid_text
from decks.builders.pictures.image import pic
from decks.design import LINE_HEIGHT, MARGIN_WIDE, RADIUS, RULE, TYPE, H, W
from decks.models.elements import Element, Line, Shape, Text
from decks.models.layout import StatementSlide
from decks.text_metrics import TextMetrics


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
        metrics = TextMetrics()
        title = metrics.fit_font_size(
            spec.title,
            76 if not figure else 56,
            (text_w, z1 - z0 - lead_h - 20),
            30,
            bold=True,
            snap=True,
        )
        title_fs = title.size
        text_h = title.lines * title_fs * LINE_HEIGHT
        author_h = 48 if spec.author else 0
        group_h = lead_h + text_h + author_h
        y0 = z0 + (z1 - z0 - group_h) / 2
        els.append(Shape(x=MARGIN_WIDE, y=y0 - 4, w=6, h=group_h + 8, fill=rule))
        if lead:
            els.append(
                mid_text(
                    x=MARGIN_WIDE + 28,
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
                x=MARGIN_WIDE + 28,
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
                    x=MARGIN_WIDE + 28,
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
                    width=RULE["thin"],
                )
            )
            figure_fs = max(40, min(120, 420 / (0.62 * len(figure_text))))
            label = " ".join(spec.label) if spec.label else ""
            label_lines = metrics.lines(label, TYPE["lead"], 420)
            label_h = label_lines * TYPE["lead"] * LINE_HEIGHT + 12 if label else 0
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
            point_w = (W - 2 * MARGIN_WIDE - 24 * (n - 1)) / n
            x = MARGIN_WIDE + (point_w + 24) * i
            els.append(Shape(x=x, y=470, w=point_w, h=130, fill="bg", radius=RADIUS["md"]))
            point_fs = metrics.fit_font_size(
                point, 26, (point_w - 56, 100), 14, bold=True, snap=True
            ).size
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
