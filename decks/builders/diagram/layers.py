"""Layer slides: stacked layers with an element row."""

from decks.builders.base import BaseBuilder
from decks.builders.common import MARGIN, RADIUS, TYPE, W, mid_text, title_el
from decks.models.diagram import LayersSlide
from decks.models.elements import Element, Shape

NAME_W = 200
GAP = 16


class LayersBuilder(BaseBuilder[LayersSlide]):
    """Render stacked layers, each with its own set of elements."""

    TYPE = "layers"
    DESCRIPTION = (
        "Use this slide to show a stack of layers. Each layer has a name and contains one or more "
        "elements. You can highlight layers."
    )
    SPEC = LayersSlide

    def build(self, spec: LayersSlide) -> list[Element]:
        n = len(spec.layers)
        highlight = (
            spec.highlight
            if isinstance(spec.highlight, list)
            else ([] if spec.highlight is None else [spec.highlight])
        )
        lh = min(96, (470 - GAP * (n - 1)) / n)
        els: list[Element] = [title_el(spec.title)]
        for i, layer in enumerate(spec.layers):
            y = 150 + (lh + GAP) * i
            active = i in highlight
            els.append(
                Shape(
                    x=MARGIN,
                    y=y,
                    w=NAME_W,
                    h=lh,
                    fill="primary" if active else "light",
                    radius=RADIUS["md"],
                )
            )
            els.append(
                mid_text(
                    x=MARGIN + 16,
                    y=y,
                    w=NAME_W - 32,
                    h=lh,
                    text=layer.name,
                    font_size=TYPE["body_l"],
                    bold=True,
                    color="bg" if active else "primary",
                )
            )
            m = max(1, len(layer.elements))
            ex = MARGIN + NAME_W + GAP
            ew = (W - MARGIN - ex - GAP * (m - 1)) / m
            for k, element in enumerate(layer.elements):
                x = ex + (ew + GAP) * k
                els.append(
                    Shape(
                        x=x,
                        y=y,
                        w=ew,
                        h=lh,
                        fill="bg",
                        stroke="primary" if active else "light",
                        stroke_width=2,
                        radius=RADIUS["md"],
                    )
                )
                els.append(
                    mid_text(
                        x=x + 8,
                        y=y,
                        w=ew - 16,
                        h=lh,
                        text=element,
                        font_size=TYPE["body"],
                        align="center",
                    )
                )
        return els
