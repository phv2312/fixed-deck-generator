"""Screenshot slides: a framed image with numbered callouts."""

from decks.builders.base import BaseBuilder
from decks.builders.common import AMBER, GREEN, MARGIN, RADIUS, RED, TYPE, W, mid_text, title_el
from decks.models.elements import Element, Shape
from decks.models.pictures import ScreenshotSlide

from .image import pic


class ScreenshotBuilder(BaseBuilder[ScreenshotSlide]):
    """Render a browser-framed screenshot with numbered callouts."""

    TYPE = "screenshot"
    DESCRIPTION = (
        "Use this slide to present a screenshot in a browser frame. Numbered callouts explain each "
        "point."
    )
    SPEC = ScreenshotSlide

    def build(self, spec: ScreenshotSlide) -> list[Element]:
        els: list[Element] = [title_el(spec.title)]
        fx, fy, fw, fh = MARGIN, 135, 770, 490
        els.append(
            Shape(
                x=fx,
                y=fy,
                w=fw,
                h=fh,
                fill="bg",
                stroke="grid",
                stroke_width=2,
                radius=RADIUS["md"],
            )
        )
        els.append(Shape(x=fx, y=fy, w=fw, h=34, fill="tint", radius=RADIUS["md"]))
        for k, color in enumerate((RED, AMBER, GREEN)):
            els.append(
                Shape(x=fx + 14 + 22 * k, y=fy + 10, w=13, h=13, shape="ellipse", fill=color)
            )
        ix, iy, iw, ih = fx + 6, fy + 40, fw - 12, fh - 46
        els += pic(spec.image, ix, iy, iw, ih, "contain")
        for i, callout in enumerate(spec.callouts):
            cx, cy = ix + callout.x * iw, iy + callout.y * ih
            els.append(
                Shape(
                    x=cx - 15,
                    y=cy - 15,
                    w=30,
                    h=30,
                    shape="ellipse",
                    fill="ink",
                    stroke="bg",
                    stroke_width=3,
                )
            )
            els.append(
                mid_text(
                    x=cx - 15,
                    y=cy - 15,
                    w=30,
                    h=30,
                    text=str(i + 1),
                    font_size=TYPE["body"],
                    bold=True,
                    color="bg",
                    align="center",
                )
            )
            ly = 150 + 56 * i
            els.append(Shape(x=870, y=ly + 4, w=30, h=30, shape="ellipse", fill="ink"))
            els.append(
                mid_text(
                    x=870,
                    y=ly + 4,
                    w=30,
                    h=30,
                    text=str(i + 1),
                    font_size=TYPE["body"],
                    bold=True,
                    color="bg",
                    align="center",
                )
            )
            els.append(
                mid_text(
                    x=912,
                    y=ly,
                    w=W - MARGIN - 912,
                    h=52,
                    text=callout.text,
                    font_size=TYPE["body"],
                )
            )
        return els
