"""Discussion slides: a question with prompts and a timebox."""

from decks.builders.base import BaseBuilder
from decks.builders.common import bullets, mid_text, title_el
from decks.design import BODY_TOP, CONTENT_W, MARGIN, RADIUS, TYPE, W
from decks.models.elements import Element, Shape, Text
from decks.models.programme import DiscussionSlide


class DiscussionBuilder(BaseBuilder[DiscussionSlide]):
    """Render a discussion question with optional prompts and timebox."""

    TYPE = "discussion"
    DESCRIPTION = (
        "Use this slide to focus a workshop or meeting discussion on one question. You can add "
        "prompts and a timebox."
    )
    SPEC = DiscussionSlide

    def build(self, spec: DiscussionSlide) -> list[Element]:
        els: list[Element] = [title_el(spec.title)]
        els.append(
            Shape(x=MARGIN, y=BODY_TOP, w=CONTENT_W, h=250, fill="primary", radius=RADIUS["md"])
        )
        els.append(
            mid_text(
                x=MARGIN + 40,
                y=BODY_TOP,
                w=CONTENT_W - 80,
                h=250,
                text=spec.question,
                font_size=TYPE["h1"] if len(spec.question) <= 60 else TYPE["h2"],
                bold=True,
                color="bg",
            )
        )
        if spec.timebox:
            els.append(
                Shape(x=W - MARGIN - 190, y=168, w=170, h=34, fill="bg", radius=RADIUS["pill"])
            )
            els.append(
                mid_text(
                    x=W - MARGIN - 190,
                    y=168,
                    w=170,
                    h=34,
                    text=f"⏱ {spec.timebox}",
                    font_size=TYPE["body"],
                    bold=True,
                    color="primary",
                    align="center",
                )
            )
        if spec.prompts:
            els.append(
                mid_text(
                    x=MARGIN,
                    y=424,
                    w=300,
                    h=28,
                    text="Prompts",
                    font_size=TYPE["small"],
                    bold=True,
                    color="muted",
                )
            )
            els.append(
                Text(
                    x=MARGIN,
                    y=456,
                    w=CONTENT_W,
                    h=170,
                    text=bullets(spec.prompts),
                    font_size=TYPE["lead"],
                )
            )
        return els
