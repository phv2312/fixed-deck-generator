"""Matrix slides: items plotted in four quadrants."""

from decks.builders.base import BaseBuilder
from decks.builders.common import TYPE, W, mid_text, title_el
from decks.models.diagram import MatrixSlide
from decks.models.elements import Element, Line, Shape, Text

PX0, PX1, PY0, PY1 = 150, 780, 150, 560
LEG_X = 830


class MatrixBuilder(BaseBuilder[MatrixSlide]):
    """Render a 2x2 matrix with labelled items."""

    TYPE = "matrix"
    DESCRIPTION = (
        "Use this slide to position items in a 2x2 matrix with named axes. You can add quadrant "
        "labels and a numbered legend."
    )
    SPEC = MatrixSlide

    def build(self, spec: MatrixSlide) -> list[Element]:
        lo, hi = spec.scale
        mw, mh = (PX1 - PX0) / 2, (PY1 - PY0) / 2
        els: list[Element] = [title_el(spec.title)]
        for k in range(4):
            r, c = divmod(k, 2)
            els.append(
                Shape(
                    x=PX0 + mw * c,
                    y=PY0 + mh * r,
                    w=mw,
                    h=mh,
                    fill="tint" if k == 1 else "bg",
                    stroke="grid",
                    stroke_width=1.5,
                )
            )
            if spec.quadrants and k < len(spec.quadrants):
                els.append(
                    Text(
                        x=PX0 + mw * c + 10,
                        y=PY0 + mh * r + 8,
                        w=mw - 20,
                        h=24,
                        text=spec.quadrants[k],
                        font_size=TYPE["small"],
                        bold=True,
                        color="muted",
                        align="left",
                    )
                )
        els.append(Line(x1=PX0, y1=PY0, x2=PX0, y2=PY1, color="primary", width=2.5))
        els.append(Line(x1=PX0, y1=PY1, x2=PX1, y2=PY1, color="primary", width=2.5))
        xa, ya = spec.x_axis, spec.y_axis
        if xa.low:
            els.append(
                Text(
                    x=PX0,
                    y=PY1 + 8,
                    w=200,
                    h=22,
                    text=xa.low,
                    font_size=TYPE["small"],
                    color="muted",
                )
            )
        if xa.high:
            els.append(
                Text(
                    x=PX1 - 200,
                    y=PY1 + 8,
                    w=200,
                    h=22,
                    text=xa.high,
                    font_size=TYPE["small"],
                    color="muted",
                    align="right",
                )
            )
        if xa.name:
            els.append(
                Text(
                    x=PX0,
                    y=PY1 + 8,
                    w=PX1 - PX0,
                    h=26,
                    text=xa.name,
                    font_size=TYPE["body"],
                    bold=True,
                    color="primary",
                    align="center",
                )
            )
        if ya.name:
            els.append(
                mid_text(
                    x=64,
                    y=PY0 - 34,
                    w=400,
                    h=24,
                    text=ya.name,
                    font_size=TYPE["body"],
                    bold=True,
                    color="primary",
                )
            )
        if ya.high:
            els.append(
                Text(
                    x=PX0 - 86,
                    y=PY0,
                    w=78,
                    h=40,
                    text=ya.high,
                    font_size=TYPE["small"],
                    color="muted",
                    align="right",
                )
            )
        if ya.low:
            els.append(
                Text(
                    x=PX0 - 86,
                    y=PY1 - 40,
                    w=78,
                    h=40,
                    text=ya.low,
                    font_size=TYPE["small"],
                    color="muted",
                    align="right",
                    valign="bottom",
                )
            )
        for i, item in enumerate(spec.items):
            fx = min(1, max(0, (item.x - lo) / ((hi - lo) or 1)))
            fy = min(1, max(0, (item.y - lo) / ((hi - lo) or 1)))
            cx = PX0 + 30 + fx * (PX1 - PX0 - 60)
            cy = PY1 - 30 - fy * (PY1 - PY0 - 60)
            hi_item = spec.highlight == i
            dot = "muted" if spec.highlight is not None and not hi_item else "primary"
            d = 40 if hi_item else 34
            els.append(
                Shape(
                    x=cx - d / 2,
                    y=cy - d / 2,
                    w=d,
                    h=d,
                    shape="ellipse",
                    fill="ink" if hi_item else "primary",
                    stroke="bg",
                    stroke_width=2,
                )
            )
            els.append(
                mid_text(
                    x=cx - d / 2,
                    y=cy - d / 2,
                    w=d,
                    h=d,
                    text=str(i + 1),
                    font_size=TYPE["small"],
                    bold=True,
                    color="bg",
                    align="center",
                )
            )
            ly = 150 + 34 * i
            els.append(Shape(x=LEG_X, y=ly + 4, w=26, h=26, shape="ellipse", fill=dot))
            els.append(
                mid_text(
                    x=LEG_X,
                    y=ly + 4,
                    w=26,
                    h=26,
                    text=str(i + 1),
                    font_size=TYPE["caption"],
                    bold=True,
                    color="bg",
                    align="center",
                )
            )
            els.append(
                mid_text(
                    x=LEG_X + 38,
                    y=ly,
                    w=W - 64 - LEG_X - 38,
                    h=34,
                    text=item.label,
                    font_size=TYPE["body"],
                    bold=hi_item,
                )
            )
        return els
