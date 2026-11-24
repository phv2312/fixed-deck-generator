"""Chart drawing service: turns a chart spec into positioned elements."""

import math
from dataclasses import dataclass
from typing import ClassVar, Literal

from decks.builders.common import arc_pts, fmt, on
from decks.design import MARGIN, RULE, TYPE
from decks.models.analytics import Chart
from decks.models.elements import Element, Line, Polygon, Shape, Text


@dataclass(frozen=True)
class SeriesStyle:
    """Fill token and opacity of one series in one category."""

    fill: str
    opacity: float


class ChartRenderer:
    """Render one chart at a fixed layout, optionally scaled into a box."""

    X0, X1 = MARGIN, 800
    Y_T, Y_B = 240, 570
    SERIES_COLORS: ClassVar[list[str]] = ["primary", "light", "accent", "tint", "ink"]
    CATEGORY_COLORS: ClassVar[list[str]] = ["primary", "light", "accent", "tint", "ink", "muted"]
    STAGE_X0, STAGE_Y0, STAGE_X1, STAGE_Y1 = MARGIN, 185.0, 800.0, 600.0

    def __init__(self, chart: Chart) -> None:
        """Store the chart to render."""
        self._chart = chart

    def render(self) -> list[Element]:
        """Render the chart at its standard layout coordinates."""
        return self._header() + self._body()

    def draw(self, x: float, y: float, w: float, h: float) -> list[Element]:
        """Draw the chart into an arbitrary box by scaling the standard layout."""
        kx = w / (self.STAGE_X1 - self.STAGE_X0)
        ky = h / (self.STAGE_Y1 - self.STAGE_Y0)

        def mx(v: float) -> float:
            return x + (v - self.STAGE_X0) * kx

        def my(v: float) -> float:
            return y + (v - self.STAGE_Y0) * ky

        out: list[Element] = []
        for element in self.render():
            if isinstance(element, (Shape, Text)):
                element = element.model_copy(
                    update={
                        "x": mx(element.x),
                        "y": my(element.y),
                        "w": element.w * kx,
                        "h": element.h * ky,
                    }
                )
            elif isinstance(element, Line):
                element = element.model_copy(
                    update={
                        "x1": mx(element.x1),
                        "y1": my(element.y1),
                        "x2": mx(element.x2),
                        "y2": my(element.y2),
                    }
                )
            elif isinstance(element, Polygon):
                element = element.model_copy(
                    update={"points": [(mx(px), my(py)) for px, py in element.points]}
                )
            out.append(element)
        return out

    def _label(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        text: str,
        *,
        size: float = TYPE["small"],
        color: str = "text",
        bold: bool = False,
        align: Literal["left", "center", "right"] = "center",
        valign: Literal["top", "middle", "bottom"] = "middle",
    ) -> Text:
        return Text(
            x=x,
            y=y,
            w=w,
            h=h,
            text=text,
            font_size=size,
            color=color,
            bold=bold,
            align=align,
            valign=valign,
        )

    def _opacity(self, index: int) -> float:
        highlight = self._chart.highlight
        return 0.4 if highlight is not None and highlight != index else 1.0

    def _colour(self, series_index: int, series_count: int, category_index: int) -> SeriesStyle:
        """Return the fill token and opacity of a series in a category."""
        chart = self._chart
        if series_count == 1:
            if chart.highlight is None:
                return SeriesStyle(fill="primary", opacity=1.0)
            fill = "primary" if chart.highlight == category_index else "light"
            return SeriesStyle(fill=fill, opacity=1.0)
        return SeriesStyle(
            fill=self.SERIES_COLORS[series_index % len(self.SERIES_COLORS)],
            opacity=self._opacity(category_index),
        )

    def _body(self) -> list[Element]:
        match self._chart.type:
            case "column":
                return self._vertical(stacked=False)
            case "stacked":
                return self._vertical(stacked=True)
            case "bar":
                return self._horizontal(stacked=False, full=False)
            case "hstacked":
                return self._horizontal(stacked=True, full=False)
            case "bar100":
                return self._horizontal(stacked=True, full=True)
            case "line":
                return self._line()
            case "doughnut":
                return self._doughnut()
            case "waterfall":
                return self._waterfall()
            case _:
                return []

    def _header(self) -> list[Element]:
        chart = self._chart
        els: list[Element] = []
        if chart.unit and chart.type != "doughnut":
            els.append(
                self._label(
                    self.X0,
                    192,
                    300,
                    22,
                    f"in {chart.unit}",
                    size=TYPE["caption"],
                    color="muted",
                    align="left",
                )
            )
        names = list(chart.named_series())
        if len(names) > 1 and chart.type not in ("doughnut", "waterfall"):
            x = self.X1 - 160 * len(names)
            for index, name in enumerate(names):
                els.append(
                    Shape(
                        x=x,
                        y=196,
                        w=14,
                        h=14,
                        fill=self.SERIES_COLORS[index % len(self.SERIES_COLORS)],
                    )
                )
                els.append(self._label(x + 20, 190, 130, 26, name, align="left"))
                x += 160
        return els

    def _vertical(self, *, stacked: bool) -> list[Element]:
        chart = self._chart
        series = list(chart.named_series().items())
        n, s = len(chart.categories), len(series)
        pos = [[max(0, v) for v in values] for _, values in series]
        totals = [sum(p[i] for p in pos) for i in range(n)]
        maxv = max(totals) if stacked else max(max(p) for p in pos)
        k = (self.Y_B - self.Y_T) / (maxv or 1)
        slot = (self.X1 - self.X0) / n
        gw = slot * 0.62
        els: list[Element] = []
        for i, cat in enumerate(chart.categories):
            cx = self.X0 + slot * (i + 0.5)
            y = self.Y_B
            for j in range(s):
                v = pos[j][i]
                h = v * k
                style = self._colour(j, s, i)
                col, opacity = style.fill, style.opacity
                if stacked:
                    y -= h
                    els.append(Shape(x=cx - gw / 2, y=y, w=gw, h=h, fill=col, opacity=opacity))
                    if chart.labels and h >= 22:
                        els.append(self._label(cx - gw / 2, y, gw, h, fmt(v), color=on(col)))
                else:
                    bw = gw / s
                    x = cx - gw / 2 + bw * j
                    els.append(Shape(x=x, y=self.Y_B - h, w=bw - 2, h=h, fill=col, opacity=opacity))
                    if chart.labels:
                        els.append(
                            self._label(x - 10, self.Y_B - h - 24, bw + 18, 22, fmt(v), bold=True)
                        )
            if stacked and chart.labels and s > 1:
                els.append(
                    self._label(
                        cx - 50, self.Y_B - totals[i] * k - 26, 100, 22, fmt(totals[i]), bold=True
                    )
                )
            els.append(
                self._label(
                    cx - slot / 2, self.Y_B + 8, slot, 24, cat, size=TYPE["caption"], color="muted"
                )
            )
        els.append(
            Line(x1=self.X0 - 6, y1=self.Y_B, x2=self.X1, y2=self.Y_B, color="muted", width=1.5)
        )
        return els

    def _horizontal(self, *, stacked: bool, full: bool) -> list[Element]:
        chart = self._chart
        series = list(chart.named_series().items())
        n, s = len(chart.categories), len(series)
        pos = [[max(0, v) for v in values] for _, values in series]
        totals = [sum(p[i] for p in pos) for i in range(n)]
        bx0, bx1 = self.X0 + 170, self.X1 - 60
        maxv = 100 if full else (max(totals) if stacked else max(max(p) for p in pos))
        k = (bx1 - bx0) / (maxv or 1)
        slot = (self.Y_B - self.Y_T + 20) / n
        bh = slot * 0.6
        els: list[Element] = []
        for i, cat in enumerate(chart.categories):
            cy = self.Y_T - 10 + slot * (i + 0.5)
            els.append(self._label(self.X0, cy - slot / 2, 160, slot, cat, align="right"))
            x = bx0
            for j in range(s):
                v = pos[j][i]
                if full:
                    v = v / (totals[i] or 1) * 100
                w = v * k
                style = self._colour(j, s, i)
                col, opacity = style.fill, style.opacity
                if stacked or full:
                    els.append(Shape(x=x, y=cy - bh / 2, w=w, h=bh, fill=col, opacity=opacity))
                    if chart.labels and w >= 34:
                        els.append(
                            self._label(
                                x,
                                cy - bh / 2,
                                w,
                                bh,
                                f"{v:.0f} %" if full else fmt(v),
                                color=on(col),
                            )
                        )
                    x += w
                else:
                    sub = bh / s
                    els.append(
                        Shape(
                            x=bx0,
                            y=cy - bh / 2 + sub * j,
                            w=w,
                            h=sub - 2,
                            fill=col,
                            opacity=opacity,
                        )
                    )
                    if chart.labels:
                        els.append(
                            self._label(
                                bx0 + w + 6,
                                cy - bh / 2 + sub * j,
                                70,
                                sub,
                                fmt(v),
                                bold=True,
                                align="left",
                            )
                        )
            if stacked and not full and chart.labels and s > 1:
                els.append(
                    self._label(x + 6, cy - 12, 70, 24, fmt(totals[i]), bold=True, align="left")
                )
        els.append(
            Line(x1=bx0, y1=self.Y_T - 14, x2=bx0, y2=self.Y_B + 8, color="muted", width=1.5)
        )
        return els

    def _line(self) -> list[Element]:
        chart = self._chart
        series = list(chart.named_series().items())
        n = len(chart.categories)
        allv = [v for _, values in series for v in values]
        ymin, ymax = min(0, min(allv)), max(allv)
        k = (self.Y_B - self.Y_T) / ((ymax - ymin) or 1)

        def yv(v: float) -> float:
            return self.Y_B - (v - ymin) * k

        slot = (self.X1 - self.X0) / n

        def cx(i: int) -> float:
            return self.X0 + slot * (i + 0.5)

        els: list[Element] = [
            Line(x1=self.X0 - 6, y1=yv(0), x2=self.X1, y2=yv(0), color="muted", width=1.5)
        ]
        for j, (_, values) in enumerate(series):
            col = self.SERIES_COLORS[j % len(self.SERIES_COLORS)] if len(series) > 1 else "primary"
            for i in range(n - 1):
                els.append(
                    Line(
                        x1=cx(i),
                        y1=yv(values[i]),
                        x2=cx(i + 1),
                        y2=yv(values[i + 1]),
                        color=col,
                        width=3.5,
                    )
                )
            for i, v in enumerate(values):
                els.append(
                    Shape(
                        x=cx(i) - 6,
                        y=yv(v) - 6,
                        w=12,
                        h=12,
                        shape="ellipse",
                        fill=col,
                        opacity=self._opacity(i),
                    )
                )
                if chart.labels:
                    els.append(self._label(cx(i) - 40, yv(v) - 30, 80, 22, fmt(v), bold=True))
        for i, cat in enumerate(chart.categories):
            els.append(
                self._label(
                    cx(i) - slot / 2,
                    self.Y_B + 8,
                    slot,
                    24,
                    cat,
                    size=TYPE["caption"],
                    color="muted",
                )
            )
        return els

    def _doughnut(self) -> list[Element]:
        chart = self._chart
        values = next(iter(chart.named_series().values()))
        total = sum(values) or 1
        cx, cy, outer, inner = self.X0 + 230, 405, 165, 98
        els: list[Element] = []
        angle = 0.0
        for i, v in enumerate(values):
            end = angle + 2 * math.pi * v / total
            points = arc_pts(cx, cy, outer, angle, end) + arc_pts(cx, cy, inner, end, angle, 28)
            els.append(
                Polygon(
                    points=points,
                    fill=self.CATEGORY_COLORS[i % len(self.CATEGORY_COLORS)],
                    stroke="bg",
                    stroke_width=RULE["thin"],
                    opacity=self._opacity(i),
                )
            )
            angle = end
        if chart.centre:
            els.append(
                self._label(
                    cx - inner,
                    cy - 40,
                    2 * inner,
                    80,
                    chart.centre,
                    size=TYPE["lead"],
                    color="primary",
                    bold=True,
                )
            )
        unit = f" {chart.unit}" if chart.unit else ""
        for i, (cat, v) in enumerate(zip(chart.categories, values, strict=False)):
            y = 290 + 40 * i
            els.append(
                Shape(
                    x=self.X0 + 470,
                    y=y + 4,
                    w=18,
                    h=18,
                    fill=self.CATEGORY_COLORS[i % len(self.CATEGORY_COLORS)],
                    opacity=self._opacity(i),
                )
            )
            els.append(
                self._label(
                    self.X0 + 498,
                    y,
                    220,
                    26,
                    f"{cat}  {fmt(v)}{unit}" if chart.labels else cat,
                    align="left",
                )
            )
        return els

    def _waterfall(self) -> list[Element]:
        chart = self._chart
        values = next(iter(chart.named_series().values()))
        totals = set(chart.totals or [])
        n = len(values)
        run, bars = 0.0, []
        for i, v in enumerate(values):
            if i in totals:
                if v != 0:
                    run = v
                bars.append((min(0, run), max(0, run), run, "total"))
            else:
                bars.append((min(run, run + v), max(run, run + v), v, "up" if v >= 0 else "down"))
                run += v
        ymin = min(0, min(b[0] for b in bars))
        ymax = max(b[1] for b in bars)
        k = (self.Y_B - self.Y_T) / ((ymax - ymin) or 1)

        def yv(v: float) -> float:
            return self.Y_B - (v - ymin) * k

        slot = (self.X1 - self.X0) / n
        bw = slot * 0.6
        els: list[Element] = [
            Line(x1=self.X0 - 6, y1=yv(0), x2=self.X1, y2=yv(0), color="muted", width=1.5)
        ]
        level = 0.0
        for i, (lo, hi, v, kind) in enumerate(bars):
            cx = self.X0 + slot * (i + 0.5)
            col = {"total": "primary", "up": "accent", "down": "ink"}[kind]
            els.append(
                Shape(
                    x=cx - bw / 2,
                    y=yv(hi),
                    w=bw,
                    h=max(2, (hi - lo) * k),
                    fill=col,
                    opacity=self._opacity(i),
                )
            )
            if chart.labels:
                text = fmt(v) if kind == "total" else f"{v:+,.10g}"
                els.append(self._label(cx - 50, yv(hi) - 26, 100, 22, text, bold=True))
            if i < n - 1:
                level = hi if kind in ("up", "total") else lo
                els.append(
                    Line(
                        x1=cx + bw / 2,
                        y1=yv(level),
                        x2=cx + slot - bw / 2,
                        y2=yv(level),
                        color="grid",
                        width=1.5,
                        dash=True,
                    )
                )
            els.append(
                self._label(
                    cx - slot / 2,
                    self.Y_B + 8,
                    slot,
                    24,
                    chart.categories[i],
                    size=TYPE["caption"],
                    color="muted",
                )
            )
        return els
