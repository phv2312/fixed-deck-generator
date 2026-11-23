"""Steps slides: an action list with owner and date columns."""

from decks.builders.base import BaseBuilder
from decks.builders.common import CONTENT_TOP, MARGIN, RADIUS, TYPE, W, banner, mid_text, title_el
from decks.models.elements import Element, Line, Shape
from decks.models.programme import StepsSlide

OWN_X, DATE_X = 780, 1010


class StepsBuilder(BaseBuilder[StepsSlide]):
    """Render an action list with owners, dates and an optional ask."""

    TYPE = "steps"
    DESCRIPTION = (
        "Use this slide for a list of actions, next steps or a checklist with owner and date "
        "columns. Mark finished steps as done. You can add a call to action at the end."
    )
    SPEC = StepsSlide

    def build(self, spec: StepsSlide) -> list[Element]:
        n = len(spec.steps)
        bottom = 560 if spec.ask else 630
        rh = min(70, (bottom - 190) / n)
        els: list[Element] = [title_el(spec.title)]
        for x, w, label in ((MARGIN, 600, "Action"), (OWN_X, 210, "Owner"), (DATE_X, 206, "Date")):
            els.append(
                mid_text(
                    x=x,
                    y=CONTENT_TOP,
                    w=w,
                    h=34,
                    text=label,
                    font_size=TYPE["small"],
                    bold=True,
                    color="muted",
                )
            )
        els.append(Line(x1=MARGIN, y1=178, x2=W - MARGIN, y2=178, color="primary", width=2))
        for i, step in enumerate(spec.steps):
            y = 186 + rh * i
            els.append(
                Shape(
                    x=MARGIN,
                    y=y + rh / 2 - 17,
                    w=34,
                    h=34,
                    shape="ellipse",
                    fill="accent" if step.done else "primary",
                )
            )
            els.append(
                mid_text(
                    x=MARGIN,
                    y=y + rh / 2 - 17,
                    w=34,
                    h=34,
                    text="✓" if step.done else str(i + 1),
                    font_size=TYPE["small"],
                    bold=True,
                    color="bg",
                    align="center",
                )
            )
            text = step.head + (f"\n{step.text}" if step.text else "")
            els.append(
                mid_text(
                    x=MARGIN + 50,
                    y=y,
                    w=540,
                    h=rh,
                    text=text,
                    font_size=TYPE["body"],
                )
            )
            if step.owner:
                els.append(
                    mid_text(
                        x=OWN_X,
                        y=y,
                        w=210,
                        h=rh,
                        text=step.owner,
                        font_size=TYPE["body"],
                    )
                )
            if step.date:
                els.append(
                    Shape(
                        x=DATE_X, y=y + rh / 2 - 15, w=140, h=30, fill="tint", radius=RADIUS["pill"]
                    )
                )
                els.append(
                    mid_text(
                        x=DATE_X,
                        y=y + rh / 2 - 15,
                        w=140,
                        h=30,
                        text=step.date,
                        font_size=TYPE["small"],
                        bold=True,
                        color="primary",
                        align="center",
                    )
                )
            els.append(Line(x1=MARGIN, y1=y + rh, x2=W - MARGIN, y2=y + rh, color="grid", width=1))
        if spec.ask:
            els += banner(spec.ask, 584)
        return els
