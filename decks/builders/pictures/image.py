"""Image placement with a placeholder for missing files."""

import os
from typing import Literal

from decks.builders.common import RADIUS, TYPE, mid_text
from decks.models.elements import Element, Image, Line, Shape


def pic(
    src: str, x: float, y: float, w: float, h: float, fit: Literal["cover", "contain"] = "cover"
) -> list[Element]:
    """Return the picture, or a labelled placeholder when the file does not exist."""
    if src.startswith(("http://", "https://", "data:")) or os.path.isfile(src):
        return [Image(src=src, x=x, y=y, w=w, h=h, fit=fit)]
    return [
        Shape(x=x, y=y, w=w, h=h, fill="grid", opacity=0.45),
        Line(x1=x, y1=y, x2=x + w, y2=y + h, color="muted", width=1),
        Line(x1=x + w, y1=y, x2=x, y2=y + h, color="muted", width=1),
        Shape(x=x + w / 2 - 150, y=y + h / 2 - 20, w=300, h=40, fill="bg", radius=RADIUS["pill"]),
        mid_text(
            x=x + w / 2 - 150,
            y=y + h / 2 - 20,
            w=300,
            h=40,
            text=f"image: {os.path.basename(src)}",
            font_size=TYPE["small"],
            color="muted",
            align="center",
        ),
    ]
