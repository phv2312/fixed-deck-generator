"""Org slides: a hierarchy of people or groups."""

from decks.builders.base import BaseBuilder
from decks.builders.common import CONTENT_W, RADIUS, TYPE, W, mid_text, title_el
from decks.models.diagram import OrgSlide, Person
from decks.models.elements import Element, Line, Shape

GAP = 24


class OrgBuilder(BaseBuilder[OrgSlide]):
    """Render an organisation chart with a head and member groups."""

    TYPE = "org"
    DESCRIPTION = (
        "Use this slide for an organisation or team hierarchy. The slide shows one head, optional "
        "groups, and the people in each group."
    )
    SPEC = OrgSlide

    def _box(
        self, x: float, y: float, w: float, h: float, person: Person, *, fill: str, fg: str
    ) -> list[Element]:
        text = person.name + (f"\n{person.role}" if person.role else "")
        return [
            Shape(x=x, y=y, w=w, h=h, fill=fill, radius=RADIUS["md"]),
            mid_text(
                x=x + 8,
                y=y,
                w=w - 16,
                h=h,
                text=text,
                font_size=TYPE["body"],
                bold=False,
                color=fg,
                align="center",
            ),
        ]

    def build(self, spec: OrgSlide) -> list[Element]:
        grouped = bool(spec.groups)
        m = len(spec.groups) if grouped else len(spec.members)
        cw = min(280, (CONTENT_W - GAP * (m - 1)) / m)
        total = cw * m + GAP * (m - 1)
        x0 = (W - total) / 2

        def cx(i: int) -> float:
            return x0 + (cw + GAP) * i + cw / 2

        els: list[Element] = [title_el(spec.title)]
        hw, hy = 320, 150
        els += self._box(W / 2 - hw / 2, hy, hw, 76, spec.head, fill="primary", fg="bg")
        bus_y = 270
        els.append(Line(x1=W / 2, y1=hy + 76, x2=W / 2, y2=bus_y, color="primary", width=2))
        if m > 1:
            els.append(Line(x1=cx(0), y1=bus_y, x2=cx(m - 1), y2=bus_y, color="primary", width=2))
        row_y = 310
        for i in range(m):
            els.append(Line(x1=cx(i), y1=bus_y, x2=cx(i), y2=row_y, color="primary", width=2))
            if grouped:
                group = spec.groups[i]
                els.append(
                    Shape(x=cx(i) - cw / 2, y=row_y, w=cw, h=46, fill="light", radius=RADIUS["md"])
                )
                els.append(
                    mid_text(
                        x=cx(i) - cw / 2,
                        y=row_y,
                        w=cw,
                        h=46,
                        text=group.label,
                        font_size=TYPE["body_l"],
                        bold=True,
                        color="primary",
                        align="center",
                    )
                )
                for k, person in enumerate(group.members):
                    els += self._box(
                        cx(i) - cw / 2, row_y + 60 + 80 * k, cw, 66, person, fill="tint", fg="text"
                    )
            else:
                els += self._box(
                    cx(i) - cw / 2, row_y, cw, 76, spec.members[i], fill="tint", fg="text"
                )
        return els
