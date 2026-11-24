"""RACI slides: responsibility assignments per activity."""

from decks.builders.base import BaseBuilder
from decks.builders.common import mid_text, title_el
from decks.design import CONTENT_TOP, CONTENT_W, MARGIN, RULE, TYPE, W
from decks.models.decisions import RaciSlide
from decks.models.elements import Element, Line, Shape

RACI_STYLE = {
    "R": ("primary", "bg"),
    "A": ("ink", "bg"),
    "C": ("light", "primary"),
    "I": ("tint", "primary"),
}


class RaciBuilder(BaseBuilder[RaciSlide]):
    """Render a RACI matrix with a legend."""

    TYPE = "raci"
    DESCRIPTION = (
        "Use this slide to assign Responsible, Accountable, Consulted and Informed roles to "
        "activities. The columns are roles or people."
    )
    SPEC = RaciSlide

    def build(self, spec: RaciSlide) -> list[Element]:
        nr, nc = len(spec.activities), len(spec.roles)
        lab_w = 340
        cw = (CONTENT_W - lab_w) / nc
        rh = min(54, 400 / nr)
        els: list[Element] = [title_el(spec.title)]
        for j, role in enumerate(spec.roles):
            els.append(
                mid_text(
                    x=MARGIN + lab_w + cw * j,
                    y=CONTENT_TOP,
                    w=cw,
                    h=50,
                    text=role,
                    font_size=TYPE["small"],
                    bold=True,
                    color="primary",
                    align="center",
                )
            )
        els.append(
            Line(x1=MARGIN, y1=194, x2=W - MARGIN, y2=194, color="primary", width=RULE["thin"])
        )
        for i, activity in enumerate(spec.activities):
            y = 198 + rh * i
            els.append(
                mid_text(
                    x=MARGIN,
                    y=y,
                    w=lab_w - 10,
                    h=rh,
                    text=activity.name,
                    font_size=TYPE["body"],
                )
            )
            for j, assignment in enumerate(activity.assignments):
                code = assignment.strip().upper().replace("R/A", "A").replace("A/R", "A")
                if code:
                    fill, fg = RACI_STYLE[code]
                    d = min(36, rh - 8)
                    cx = MARGIN + lab_w + cw * (j + 0.5)
                    els.append(
                        Shape(
                            x=cx - d / 2, y=y + rh / 2 - d / 2, w=d, h=d, shape="ellipse", fill=fill
                        )
                    )
                    els.append(
                        mid_text(
                            x=cx - d / 2,
                            y=y + rh / 2 - d / 2,
                            w=d,
                            h=d,
                            text=code,
                            font_size=TYPE["small"],
                            bold=True,
                            color=fg,
                            align="center",
                        )
                    )
            els.append(
                Line(
                    x1=MARGIN, y1=y + rh, x2=W - MARGIN, y2=y + rh, color="grid", width=RULE["hair"]
                )
            )
        ly = 198 + rh * nr + 22
        x = MARGIN
        for code, name in (
            ("R", "Responsible"),
            ("A", "Accountable"),
            ("C", "Consulted"),
            ("I", "Informed"),
        ):
            fill, fg = RACI_STYLE[code]
            els.append(Shape(x=x, y=ly, w=26, h=26, shape="ellipse", fill=fill))
            els.append(
                mid_text(
                    x=x,
                    y=ly,
                    w=26,
                    h=26,
                    text=code,
                    font_size=TYPE["caption"],
                    bold=True,
                    color=fg,
                    align="center",
                )
            )
            els.append(
                mid_text(
                    x=x + 34,
                    y=ly,
                    w=130,
                    h=26,
                    text=name,
                    font_size=TYPE["small"],
                    color="muted",
                )
            )
            x += 180
        return els
