"""Driver tree slides: a root metric decomposed into drivers."""

from decks.builders.base import BaseBuilder
from decks.builders.common import mid_text, title_el
from decks.design import BODY_TOP, CONTENT_W, MARGIN, RADIUS, TYPE
from decks.models.diagram import DriverNode, DriverTreeSlide
from decks.models.elements import Element, Line, Shape


class DriverTreeBuilder(BaseBuilder[DriverTreeSlide]):
    """Render a left-to-right driver tree with operator badges."""

    TYPE = "drivertree"
    DESCRIPTION = (
        "Use this slide to divide a root metric into sub-drivers and leaves. You can also show the "
        "operation that combines each branch."
    )
    SPEC = DriverTreeSlide

    def build(self, spec: DriverTreeSlide) -> list[Element]:
        def depth(node: DriverNode) -> int:
            return 1 + max((depth(child) for child in node.children), default=0)

        def leaves(node: DriverNode) -> int:
            return 1 if not node.children else sum(leaves(child) for child in node.children)

        levels, leaf_count = depth(spec.root), leaves(spec.root)
        bw = min(230, (CONTENT_W - 70 * (levels - 1)) / levels)
        gap = (CONTENT_W - bw * levels) / max(1, levels - 1) if levels > 1 else 0
        unit = min(96, 450 / leaf_count)
        top = BODY_TOP + (450 - unit * leaf_count) / 2
        els: list[Element] = [title_el(spec.title)]
        cursor = [top]

        def place(node: DriverNode, level: int) -> float:
            children = node.children
            if children:
                ys = [place(child, level + 1) for child in children]
                cy = (ys[0] + ys[-1]) / 2
            else:
                cy = cursor[0] + unit / 2
                cursor[0] += unit
            x = MARGIN + (bw + gap) * level
            hi = spec.highlight == node.label
            bh = min(unit - 12, 74)
            els.append(
                Shape(
                    x=x,
                    y=cy - bh / 2,
                    w=bw,
                    h=bh,
                    fill="primary" if hi else ("tint" if level else "light"),
                    radius=RADIUS["md"],
                )
            )
            text = node.label + (f"\n{node.value}" if node.value else "")
            els.append(
                mid_text(
                    x=x + 8,
                    y=cy - bh / 2,
                    w=bw - 16,
                    h=bh,
                    text=text,
                    font_size=TYPE["small"],
                    bold=True,
                    color="bg" if hi else "primary",
                    align="center",
                )
            )
            if children:
                bx = x + bw + gap * 0.5
                for _child, y2 in zip(children, ys, strict=False):
                    els.append(Line(x1=bx, y1=y2, x2=x + bw + gap, y2=y2, color="muted", width=1.5))
                els.append(Line(x1=x + bw, y1=cy, x2=bx, y2=cy, color="muted", width=1.5))
                if len(ys) > 1:
                    els.append(Line(x1=bx, y1=ys[0], x2=bx, y2=ys[-1], color="muted", width=1.5))
                if node.op:
                    op = {"x": "×", "*": "×", "-": "−"}.get(node.op, node.op)
                    els.append(Shape(x=bx - 14, y=cy - 14, w=28, h=28, shape="ellipse", fill="ink"))
                    els.append(
                        mid_text(
                            x=bx - 14,
                            y=cy - 14,
                            w=28,
                            h=28,
                            text=op,
                            font_size=TYPE["body_l"],
                            bold=True,
                            color="bg",
                            align="center",
                        )
                    )
            return cy

        place(spec.root, 0)
        return els
