"""Agenda slides: numbered items with a current marker."""

from decks.builders.base import BaseBuilder
from decks.builders.common import CONTENT_W, MARGIN, RADIUS, TYPE, W, mid_text, snap_down, title_el
from decks.models.elements import Element, Line, Shape, Text
from decks.models.layout import AgendaSlide


class AgendaBuilder(BaseBuilder[AgendaSlide]):
    """Render an agenda with a highlighted current item."""

    TYPE = "agenda"
    DESCRIPTION = (
        "Use this slide for an agenda or chapter list. The items are numbered or have icons. Give "
        "items a time or owner for a timed agenda table. You can mark the current item."
    )
    SPEC = AgendaSlide

    def _lead(self, lead: list[str], y: float = 110) -> Text:
        return mid_text(
            x=MARGIN,
            y=y,
            w=CONTENT_W,
            h=36,
            text=" ".join(lead),
            font_size=TYPE["lead"],
            color="muted",
        )

    def build(self, spec: AgendaSlide) -> list[Element]:
        if any(item.time or item.owner for item in spec.items):
            return self._table(spec)
        return self._numbered(spec)

    def _numbered(self, spec: AgendaSlide) -> list[Element]:
        n = len(spec.items)
        els: list[Element] = [title_el(spec.title)]
        if spec.lead:
            els.append(self._lead(spec.lead))
        top = 170
        rh = min(96, 450 / n)
        fs = TYPE["h3"] if rh >= 76 else (TYPE["lead"] if rh >= 56 else TYPE["body_l"])
        d = min(52, rh - 12)
        tw = CONTENT_W - 90
        for i, item in enumerate(spec.items):
            y = top + rh * i
            current = spec.current == i
            dim = spec.current is not None and not current
            if current:
                els.append(
                    Shape(
                        x=MARGIN - 16,
                        y=y + 2,
                        w=CONTENT_W + 32,
                        h=rh - 4,
                        fill="tint",
                        radius=RADIUS["md"],
                    )
                )
                els.append(Shape(x=MARGIN - 16, y=y + 2, w=6, h=rh - 4, fill="primary", radius=0))
            cy = y + rh / 2 - d / 2
            els.append(
                Shape(
                    x=MARGIN + 4,
                    y=cy,
                    w=d,
                    h=d,
                    shape="ellipse",
                    fill="light" if dim else "primary",
                )
            )
            els.append(
                mid_text(
                    x=MARGIN + 4,
                    y=cy,
                    w=d,
                    h=d,
                    text=item.icon or str(i + 1),
                    font_size=snap_down(d * 0.43),
                    bold=True,
                    color="primary" if dim else "bg",
                    align="center",
                )
            )
            els.append(
                mid_text(
                    x=MARGIN + 4 + d + 24,
                    y=y,
                    w=tw - d,
                    h=rh,
                    text=item.text,
                    font_size=fs,
                    bold=current,
                    color="muted" if dim else ("primary" if current else "text"),
                )
            )
            if i < n - 1 and not current and spec.current != i + 1:
                els.append(
                    Line(
                        x1=MARGIN + d + 28,
                        y1=y + rh,
                        x2=W - MARGIN,
                        y2=y + rh,
                        color="grid",
                        width=1,
                    )
                )
        return els

    def _table(self, spec: AgendaSlide) -> list[Element]:
        """Render a timed agenda with time, topic and owner columns."""
        n = len(spec.items)
        els: list[Element] = [title_el(spec.title)]
        if spec.lead:
            els.append(self._lead(spec.lead))
        cols = ((MARGIN + 12, 130, "Time"), (230, 680, "Topic"), (940, 276, "Owner"))
        for x, w, label in cols:
            els.append(
                mid_text(
                    x=x,
                    y=168,
                    w=w,
                    h=30,
                    text=label,
                    font_size=TYPE["small"],
                    bold=True,
                    color="muted",
                )
            )
        els.append(Line(x1=MARGIN, y1=202, x2=W - MARGIN, y2=202, color="primary", width=2.5))
        rh = min(76, 410 / n)
        fs = TYPE["lead"] if rh >= 70 else TYPE["body_l"] if rh >= 42 else TYPE["body"]
        for i, row in enumerate(spec.items):
            y = 210 + rh * i
            current = spec.current == i
            if current:
                els.append(
                    Shape(
                        x=MARGIN - 8,
                        y=y + 2,
                        w=CONTENT_W + 16,
                        h=rh - 4,
                        fill="primary",
                        radius=RADIUS["md"],
                    )
                )
            fg = "bg" if current else "text"
            ph = min(30, rh - 10)
            els.append(
                Shape(
                    x=MARGIN + 12,
                    y=y + rh / 2 - ph / 2,
                    w=96,
                    h=ph,
                    fill="bg" if current else "tint",
                    radius=RADIUS["pill"],
                )
            )
            els.append(
                mid_text(
                    x=MARGIN + 12,
                    y=y + rh / 2 - ph / 2,
                    w=96,
                    h=ph,
                    text=row.time,
                    font_size=TYPE["small"],
                    bold=True,
                    color="primary",
                    align="center",
                )
            )
            els.append(
                mid_text(
                    x=230,
                    y=y,
                    w=680,
                    h=rh,
                    text=row.text,
                    font_size=fs,
                    bold=current,
                    color=fg,
                )
            )
            if row.owner:
                els.append(
                    mid_text(
                        x=940,
                        y=y,
                        w=276,
                        h=rh,
                        text=row.owner,
                        font_size=snap_down(fs - 2),
                        color=fg,
                    )
                )
            if i < n - 1 and not current and spec.current != i + 1:
                els.append(
                    Line(x1=MARGIN, y1=y + rh, x2=W - MARGIN, y2=y + rh, color="grid", width=1)
                )
        return els
