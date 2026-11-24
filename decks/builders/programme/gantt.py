"""Gantt slides: a plan over time."""

from decks.builders.base import BaseBuilder
from decks.builders.common import mid_text, title_el
from decks.design import CONTENT_TOP, MARGIN, RADIUS, RULE, TYPE, W
from decks.models.elements import Element, Line, Polygon, Shape
from decks.models.programme import GanttRow, GanttSlide


class GanttBuilder(BaseBuilder[GanttSlide]):
    """Render a Gantt chart with groups, progress and milestones."""

    TYPE = "gantt"
    DESCRIPTION = (
        "Use this slide for a project plan over time with grouped rows and bars that span periods. "
        "You can add progress percentages, milestones and a today marker."
    )
    SPEC = GanttSlide

    def build(self, spec: GanttSlide) -> list[Element]:
        n = len(spec.periods)
        lab_w = 260
        gx0, gx1 = MARGIN + lab_w, W - MARGIN
        pw = (gx1 - gx0) / n

        def px(v: float) -> float:
            return gx0 + pw * v

        lines: list[tuple[str, GanttRow | str]] = []
        last = None
        for row in spec.rows:
            if row.group and row.group != last:
                lines.append(("group", row.group))
                last = row.group
            lines.append(("row", row))
        top = 200 + (34 if spec.milestones else 0)
        rh = min(44, (620 - top) / len(lines))
        els: list[Element] = [title_el(spec.title)]
        for j, period in enumerate(spec.periods):
            els.append(
                mid_text(
                    x=px(j),
                    y=CONTENT_TOP,
                    w=pw,
                    h=36,
                    text=period,
                    font_size=TYPE["caption"] if n > 12 else TYPE["small"],
                    bold=True,
                    color="primary",
                    align="center",
                )
            )
            els.append(
                Line(
                    x1=px(j),
                    y1=176,
                    x2=px(j),
                    y2=top + rh * len(lines),
                    color="grid",
                    width=RULE["hair"],
                )
            )
        els.append(
            Line(
                x1=px(n),
                y1=176,
                x2=px(n),
                y2=top + rh * len(lines),
                color="grid",
                width=RULE["hair"],
            )
        )
        els.append(Line(x1=MARGIN, y1=178, x2=gx1, y2=178, color="primary", width=2.5))
        if spec.milestones:
            els.append(
                mid_text(
                    x=MARGIN,
                    y=182,
                    w=lab_w,
                    h=30,
                    text="Milestones",
                    font_size=TYPE["small"],
                    bold=True,
                    color="muted",
                )
            )
            for milestone in spec.milestones:
                x, y = px(milestone.at), 197
                els.append(
                    Polygon(points=[(x, y - 11), (x + 11, y), (x, y + 11), (x - 11, y)], fill="ink")
                )
                els.append(
                    mid_text(
                        x=x + 14,
                        y=y - 12,
                        w=180,
                        h=24,
                        text=milestone.label,
                        font_size=TYPE["caption"],
                        bold=True,
                        color="ink",
                    )
                )
        for i, (_, obj) in enumerate(lines):
            y = top + rh * i
            if isinstance(obj, str):
                els.append(
                    mid_text(
                        x=MARGIN,
                        y=y,
                        w=lab_w,
                        h=rh,
                        text=obj,
                        font_size=TYPE["small"],
                        bold=True,
                        color="primary",
                    )
                )
            else:
                row = obj
                els.append(
                    mid_text(
                        x=MARGIN + (16 if row.group else 0),
                        y=y,
                        w=lab_w - 20,
                        h=rh,
                        text=row.name,
                        font_size=TYPE["body"],
                    )
                )
                x1, x2 = px(row.start), px(row.end + 1)
                bh = min(24, rh - 12)
                els.append(
                    Shape(
                        x=x1 + 2,
                        y=y + (rh - bh) / 2,
                        w=x2 - x1 - 4,
                        h=bh,
                        fill="light" if row.progress is not None else "primary",
                        radius=RADIUS["sm"],
                    )
                )
                if row.progress:
                    els.append(
                        Shape(
                            x=x1 + 2,
                            y=y + (rh - bh) / 2,
                            w=max(8, (x2 - x1 - 4) * row.progress / 100),
                            h=bh,
                            fill="primary",
                            radius=RADIUS["sm"],
                        )
                    )
                if row.progress is not None and bh >= 18:
                    els.append(
                        mid_text(
                            x=x2 + 4,
                            y=y,
                            w=60,
                            h=rh,
                            text=f"{row.progress:g} %",
                            font_size=TYPE["caption"],
                            color="muted",
                        )
                    )
            els.append(Line(x1=MARGIN, y1=y + rh, x2=gx1, y2=y + rh, color="grid", width=0.5))
        if spec.today is not None:
            x = px(spec.today)
            els.append(
                Line(
                    x1=x,
                    y1=178,
                    x2=x,
                    y2=top + rh * len(lines),
                    color="ink",
                    width=RULE["thin"],
                    dash=True,
                )
            )
            els.append(
                Shape(
                    x=x - 28,
                    y=top + rh * len(lines) + 4,
                    w=56,
                    h=22,
                    fill="ink",
                    radius=RADIUS["pill"],
                )
            )
            els.append(
                mid_text(
                    x=x - 28,
                    y=top + rh * len(lines) + 4,
                    w=56,
                    h=22,
                    text="Today",
                    font_size=TYPE["caption"],
                    bold=True,
                    color="bg",
                    align="center",
                )
            )
        return els
