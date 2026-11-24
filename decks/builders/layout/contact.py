"""Contact slides: people cards with contact details."""

import math
import os

from decks.builders.base import BaseBuilder
from decks.builders.common import (
    CONTENT_W,
    MARGIN,
    RADIUS,
    SPACE,
    TYPE,
    W,
    background,
    deco_blocks,
    mid_text,
    snap_down,
    title_el,
)
from decks.design import LINE_HEIGHT
from decks.models.elements import Element, Image, Line, Shape, Text
from decks.models.layout import ContactSlide
from decks.text_metrics import TextMetrics

LM = 80


class ContactBuilder(BaseBuilder[ContactSlide]):
    """Render one to many contact cards."""

    TYPE = "contact"
    DESCRIPTION = (
        "Use this slide to close a deck with contact details. Each person has a role, an "
        "email address and a phone number. Give people a photo or a short text to introduce a "
        "team of up to 8 as a grid."
    )
    SPEC = ContactSlide

    def build(self, spec: ContactSlide) -> list[Element]:
        if any(person.photo or person.text for person in spec.people):
            return self._team(spec)
        return self._cards(spec)

    def _cards(self, spec: ContactSlide) -> list[Element]:
        n = len(spec.people)
        els = background("tint")
        if n <= 3:
            els += deco_blocks()
        els.append(
            mid_text(
                x=LM,
                y=60,
                w=900,
                h=90,
                text=spec.title,
                font_size=TYPE["h1"],
                bold=True,
                color="primary",
            )
        )
        els.append(Line(x1=LM, y1=164, x2=LM + 90, y2=164, color="accent", width=4))
        cols = n if n <= 3 else 3
        if n == 1:
            cols = 1
        gap = 24
        name_fs, role_fs, card_h = (
            (TYPE["h3"], TYPE["body_l"], 240)
            if n == 1
            else ((TYPE["h3"], TYPE["body"], 200) if n <= 3 else (TYPE["lead"], TYPE["small"], 190))
        )
        cw = 620 if n == 1 else (440 if n == 2 else (W - 2 * LM - gap * (cols - 1)) / cols)
        metrics = TextMetrics()
        for i, person in enumerate(spec.people):
            r, c = divmod(i, cols)
            x, y = LM + (cw + gap) * c, 210 + (card_h + gap) * r
            els.append(Shape(x=x, y=y, w=cw, h=card_h, fill="bg", radius=RADIUS["md"]))
            lines_count = metrics.lines(person.name, name_fs, cw - 56, bold=True)
            els.append(
                Text(
                    x=x + 28,
                    y=y + 28,
                    w=cw - 56,
                    h=name_fs * LINE_HEIGHT * lines_count,
                    text=person.name,
                    font_size=name_fs,
                    bold=True,
                    color="primary",
                    valign="top",
                )
            )
            next_y = y + 28 + name_fs * LINE_HEIGHT * lines_count + 6
            if person.role:
                els.append(
                    mid_text(
                        x=x + 28,
                        y=next_y,
                        w=cw - 56,
                        h=role_fs * 1.5,
                        text=person.role,
                        font_size=role_fs,
                        color="muted",
                    )
                )
                next_y += role_fs * 1.5 + 12
            contact_lines = [line for line in (person.mail, person.phone) if line]
            if contact_lines:
                els.append(
                    Line(
                        x1=x + 28, y1=next_y + 4, x2=x + 68, y2=next_y + 4, color="accent", width=2
                    )
                )
                els.append(
                    Text(
                        x=x + 28,
                        y=next_y + 16,
                        w=cw - 56,
                        h=len(contact_lines) * role_fs * 1.5,
                        text="\n".join(contact_lines),
                        font_size=role_fs,
                        color="text",
                    )
                )
        return els

    def _team(self, spec: ContactSlide) -> list[Element]:
        """Render a team grid with photos or initials."""
        n = len(spec.people)
        per = n if n <= 4 else math.ceil(n / 2)
        rows = math.ceil(n / per)
        gap = SPACE["m"]
        cw = (CONTENT_W - gap * (per - 1)) / per
        ch = (470 - gap * (rows - 1)) / rows
        els: list[Element] = [title_el(spec.title)]
        for i, person in enumerate(spec.people):
            r, c = divmod(i, per)
            x, y = MARGIN + (cw + gap) * c, 140 + (ch + gap) * r
            els.append(Line(x1=x, y1=y, x2=x + cw, y2=y, color="primary", width=2))
            d = min(96, ch * 0.34)
            ax, ay = x + cw / 2 - d / 2, y + 16
            if person.photo and (person.photo.startswith("http") or os.path.isfile(person.photo)):
                els.append(Image(src=person.photo, x=ax, y=ay, w=d, h=d, fit="cover"))
            else:
                els.append(Shape(x=ax, y=ay, w=d, h=d, shape="ellipse", fill="primary"))
                initials = "".join(word[0] for word in person.name.split()[:2]).upper()
                els.append(
                    mid_text(
                        x=ax,
                        y=ay,
                        w=d,
                        h=d,
                        text=initials,
                        font_size=snap_down(d * 0.38),
                        bold=True,
                        color="bg",
                        align="center",
                    )
                )
            ty = ay + d + 8
            els.append(
                mid_text(
                    x=x + 10,
                    y=ty,
                    w=cw - 20,
                    h=28,
                    text=person.name,
                    font_size=TYPE["body_l"],
                    bold=True,
                    color="primary",
                    align="center",
                )
            )
            if person.role:
                els.append(
                    mid_text(
                        x=x + 10,
                        y=ty + 28,
                        w=cw - 20,
                        h=24,
                        text=person.role,
                        font_size=TYPE["small"],
                        color="muted",
                        align="center",
                    )
                )
            if person.text:
                els.append(
                    Text(
                        x=x + 14,
                        y=ty + 58,
                        w=cw - 28,
                        h=y + ch - (ty + 58) - 8,
                        text=person.text,
                        font_size=TYPE["small"],
                        align="center",
                    )
                )
        return els
