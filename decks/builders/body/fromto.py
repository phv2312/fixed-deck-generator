"""From/to slides: two aligned columns."""

from decks.builders.base import BaseBuilder
from decks.builders.common import CONTENT_TOP, MARGIN, RADIUS, TYPE, icon_badge, mid_text, title_el
from decks.models.body import FromToSlide
from decks.models.elements import Element, Line, Polygon, Shape

LX, LW = MARGIN, 480
RX, RW = 700, 516


class FromToBuilder(BaseBuilder[FromToSlide]):
    """Render a before/after or from/to comparison in two columns."""

    TYPE = "fromto"
    DESCRIPTION = (
        "Use this slide to compare a current state with a future state side by side. Each row has "
        "one aligned item."
    )
    SPEC = FromToSlide

    def build(self, spec: FromToSlide) -> list[Element]:
        n = len(spec.left.items)
        els: list[Element] = [title_el(spec.title)]
        for side, x, w, col in ((spec.left, LX, LW, "grid"), (spec.right, RX, RW, "light")):
            els.append(
                mid_text(
                    x=x,
                    y=CONTENT_TOP,
                    w=w,
                    h=34,
                    text=side.head,
                    font_size=TYPE["body_l"],
                    bold=True,
                    color="primary",
                )
            )
            els.append(Line(x1=x, y1=180, x2=x + w, y2=180, color=col, width=4))
        row_h = min(110, 420 / n)
        for i in range(n):
            y = 206 + row_h * i
            h = row_h - 16
            for side, x, w, fill in ((spec.left, LX, LW, None), (spec.right, RX, RW, "tint")):
                if fill:
                    els.append(Shape(x=x, y=y, w=w, h=h, fill=fill, radius=RADIUS["md"]))
                else:
                    els.append(
                        Line(x1=x, y1=y + h + 8, x2=x + w, y2=y + h + 8, color="grid", width=1)
                    )
                off = 16
                if side.icon:
                    els += icon_badge(x + 14, y + h / 2 - 16, 32, side.icon)
                    off = 60
                els.append(
                    mid_text(
                        x=x + off,
                        y=y,
                        w=w - off - 14,
                        h=h,
                        text=side.items[i],
                        font_size=TYPE["body"],
                    )
                )
            ay = y + h / 2
            els.append(
                Polygon(
                    points=[(LX + LW + 40, ay - 14), (LX + LW + 40, ay + 14), (LX + LW + 66, ay)],
                    fill="primary",
                )
            )
        return els
