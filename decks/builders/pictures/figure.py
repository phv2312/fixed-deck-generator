"""Figure slides: one picture across the slide, with a caption and a source."""

from decks.builders.base import BaseBuilder
from decks.builders.common import mid_text, title_el
from decks.design import CONTENT_W, MARGIN, TYPE, H, W
from decks.models.elements import Element, Shape
from decks.models.pictures import FigureSlide

from .image import pic

IMAGE_Y = 112
IMAGE_H = 440


class FigureBuilder(BaseBuilder[FigureSlide]):
    """Render a full-width figure with a caption and an optional source."""

    TYPE = "figure"
    DESCRIPTION = (
        "Use this slide to present one picture across the full width, with a caption and a "
        "source. The picture carries its own labels and notes: the slide has no side text. Set "
        "bleed for a full-bleed photograph with the title in a dark band."
    )
    SPEC = FigureSlide

    def build(self, spec: FigureSlide) -> list[Element]:
        if spec.bleed:
            return self._bleed(spec)
        return self._framed(spec)

    def _framed(self, spec: FigureSlide) -> list[Element]:
        width = CONTENT_W
        els: list[Element] = [title_el(spec.title)]
        els += pic(spec.image, MARGIN, IMAGE_Y, width, IMAGE_H, "contain")
        if spec.caption:
            els.append(
                mid_text(
                    x=MARGIN,
                    y=IMAGE_Y + IMAGE_H + 4,
                    w=width,
                    h=30,
                    text=spec.caption,
                    font_size=TYPE["body_l"],
                    italic=True,
                    color="primary",
                    align="center",
                )
            )
        if spec.source:
            els.append(
                mid_text(
                    x=MARGIN,
                    y=IMAGE_Y + IMAGE_H + 34,
                    w=width,
                    h=24,
                    text=f"Source: {spec.source}",
                    font_size=TYPE["caption"],
                    color="muted",
                    align="center",
                )
            )
        return els

    def _bleed(self, spec: FigureSlide) -> list[Element]:
        """Render a full-bleed picture with the title in a dark band."""
        els = pic(spec.image, 0, 0, W, H)
        els.append(Shape(x=0, y=H - 190, w=W, h=190, fill="ink", opacity=0.62))
        els.append(
            mid_text(
                x=MARGIN,
                y=H - 175,
                w=CONTENT_W,
                h=90,
                text=spec.title,
                font_size=TYPE["h1"] if len(spec.title) <= 40 else TYPE["h2"],
                bold=True,
                color="bg",
            )
        )
        if spec.caption:
            els.append(
                mid_text(
                    x=MARGIN,
                    y=H - 80,
                    w=CONTENT_W,
                    h=40,
                    text=spec.caption,
                    font_size=TYPE["lead"],
                    color="light",
                    align="center",
                )
            )
        return els
