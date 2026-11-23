import math
from functools import partial

from decks.design import (  # noqa: F401  (re-exported for builders)
    AMBER,
    BANNER_H,
    BANNER_Y,
    CONTENT_TOP,
    CONTENT_W,
    GREEN,
    GREY,
    GUTTER,
    MARGIN,
    RADIUS,
    RED,
    SPACE,
    TITLE_H,
    TITLE_Y,
    TYPE,
    H,
    W,
    snap_down,
)
from decks.models.elements import BULLET, Text
from decks.text_metrics import TextMetrics

# A Text that is vertically centred: what nearly every label in a builder wants.
mid_text = partial(Text, valign="middle")


def nice_range(lo: float, hi: float, target_ticks: int = 5) -> tuple[float, float, float]:
    """Return (min, max, step) with round tick values covering [lo, hi] plus padding."""
    if hi == lo:  # single value: pad so the range is not degenerate
        pad = abs(lo) * 0.5 or 1
        lo, hi = lo - pad, hi + pad
    span = hi - lo
    raw = span / target_ticks
    mag = 10 ** math.floor(math.log10(raw))
    step = next(m * mag for m in (1, 2, 5, 10) if m * mag >= raw)
    nlo = math.floor((lo - 0.1 * span) / step) * step
    nhi = math.ceil((hi + 0.1 * span) / step) * step
    return nlo, nhi, step


def fmt(v: float) -> str:
    return f"{v:,.10g}"


DARK = {"primary", "ink", "accent"}


def on(fill: str) -> str:
    """Readable text color token for a given fill token."""
    return "bg" if fill in DARK else "text"


def title_el(title: str) -> Text:
    size = TextMetrics().fit_font_size(title, TYPE["h2"], (CONTENT_W, TITLE_H), bold=True)
    return mid_text(
        x=MARGIN,
        y=TITLE_Y,
        w=CONTENT_W,
        h=TITLE_H,
        text=title,
        font_size=size,
        bold=True,
        color="primary",
    )


def bullets(items: list[str]) -> str:
    return "\n".join(f"{BULLET}{i}" for i in items)


def arc_pts(
    cx: float, cy: float, r: float, a0: float, a1: float, n: int = 28
) -> list[tuple[float, float]]:
    """Points on an arc; angle 0 = 12 o'clock, clockwise, radians."""
    return [
        (cx + r * math.sin(a0 + (a1 - a0) * k / n), cy - r * math.cos(a0 + (a1 - a0) * k / n))
        for k in range(n + 1)
    ]


def icon_badge(x: float, y: float, d: float, icon: str, fill: str = "accent") -> list:
    from decks.models.elements import Shape

    return [
        Shape(x=x, y=y, w=d, h=d, shape="ellipse", fill=fill),
        mid_text(
            x=x,
            y=y,
            w=d,
            h=d,
            text=icon,
            font_size=snap_down(d * 0.5),
            bold=True,
            color="primary" if fill == "bg" else on(fill),
            align="center",
        ),
    ]


def trapezoid(xc: float, y0: float, y1: float, w0: float, w1: float) -> list[tuple[float, float]]:
    return [(xc - w0 / 2, y0), (xc + w0 / 2, y0), (xc + w1 / 2, y1), (xc - w1 / 2, y1)]


def banner(text: str, y: float = BANNER_Y, h: float = BANNER_H) -> list:
    from decks.models.elements import Shape

    return [
        Shape(x=MARGIN, y=y, w=CONTENT_W, h=h, fill="primary", radius=RADIUS["md"]),
        mid_text(
            x=MARGIN + 24,
            y=y,
            w=CONTENT_W - 48,
            h=h,
            text=text,
            font_size=TYPE["body_l"],
            bold=True,
            color="bg",
            align="center",
        ),
    ]


def background(fill: str = "tint") -> list:
    from decks.models.elements import Shape

    return [Shape(x=0, y=0, w=W, h=H, fill=fill)]


def deco_blocks(
    *, sizes: tuple[int, ...] = (96, 56, 28), gap: int = SPACE["s"], inset: int = MARGIN
) -> list:
    from decks.models.elements import Shape

    opacities = (1.0, 0.55, 0.25)
    blocks: list = []
    x_right = W - inset
    for i, size in enumerate(sizes):
        blocks.append(
            Shape(
                id=f"deco-stack-{i}",
                x=x_right - size,
                y=H - inset - size,
                w=size,
                h=size,
                fill="accent",
                opacity=opacities[min(i, len(opacities) - 1)],
            )
        )
        x_right -= size + gap
    return blocks


# traffic-light wording -> (hex colour, glyph); shared by tracker and scorecard
WORDS = {
    GREEN: ("green", "ok", "done", "complete", "on track", "in plan", "good"),
    AMBER: ("amber", "yellow", "risk", "warning", "attention", "partly"),
    RED: ("red", "late", "blocked", "delay", "critical", "off track"),
}


def colour(state: str) -> tuple[str, str]:
    s = state.lower()
    for col, words in WORDS.items():
        if any(w in s for w in words):
            return col, {GREEN: "✓", AMBER: "!", RED: "✕"}[col]
    return GREY, "·"
