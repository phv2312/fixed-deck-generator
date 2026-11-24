"""Title slides: opening slide with optional image, subtitle and meta."""

from decks.builders.base import BaseBuilder
from decks.builders.common import TYPE, H, W, background, deco_blocks
from decks.builders.pictures.image import pic
from decks.design import LINE_HEIGHT
from decks.models.elements import Element, Line, Shape, Text
from decks.models.layout import TitleSlide
from decks.text_metrics import TextMetrics

LM = 80


class TitleBuilder(BaseBuilder[TitleSlide]):
    """Render a title slide with optional side image and meta line."""

    TYPE = "title"
    DESCRIPTION = (
        "Use this slide to open a deck with its title. You can add a subtitle, metadata and a side "
        "image."
    )
    SPEC = TitleSlide

    def build(self, spec: TitleSlide) -> list[Element]:
        els = background("tint")
        if spec.image:
            els += pic(spec.image, W * 0.48, 0, W * 0.52, H)
            text_w = W * 0.48 - LM - 40
        else:
            els += deco_blocks()
            text_w = 780
        subtitle = "\n".join(spec.subtitle) if spec.subtitle else ""
        sub_fs = TYPE["lead"]
        metrics = TextMetrics()
        sub_h = metrics.height(subtitle, sub_fs, text_w) + 8 if subtitle else 0
        top, bottom = 110, 560
        available = bottom - top - (sub_h + 24 if subtitle else 0)
        title = metrics.fit_font_size(
            spec.title,
            64 if not spec.image else 54,
            (text_w, available),
            30,
            bold=True,
            snap=True,
        )
        title_fs = title.size
        text_h = title.lines * title_fs * LINE_HEIGHT
        group_h = text_h + (sub_h + 24 if subtitle else 0) + 40
        y0 = top + max(0, (bottom - top - group_h) / 2)
        els.append(Shape(x=LM, y=y0, w=90, h=6, fill="accent"))
        els.append(
            Text(
                x=LM,
                y=y0 + 34,
                w=text_w,
                h=text_h + 6,
                text=spec.title,
                font_size=title_fs,
                bold=True,
                color="primary",
                valign="top",
            )
        )
        if subtitle:
            els.append(
                Text(
                    x=LM,
                    y=y0 + 34 + text_h + 24,
                    w=text_w,
                    h=sub_h,
                    text=subtitle,
                    font_size=sub_fs,
                    color="text",
                )
            )
        if spec.meta:
            meta = "\n".join(spec.meta)
            els.append(Line(x1=LM, y1=596, x2=LM + text_w, y2=596, color="grid", width=1))
            els.append(
                Text(
                    x=LM,
                    y=604,
                    w=min(text_w, 760),
                    h=70,
                    text=meta,
                    font_size=TYPE["body_l"],
                    color="muted",
                    valign="top",
                )
            )
        return els
