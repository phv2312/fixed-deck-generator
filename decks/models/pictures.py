"""family=pictures: slides built around a picture. `image` is a file path or URL; a missing file
renders a labelled placeholder so decks work before the pictures exist."""

from __future__ import annotations

from typing import Literal

from pydantic import (
    BaseModel,
    Field,
)

from .base import Text


class Callout(BaseModel):
    x: float = Field(
        ge=0, le=1, description="Horizontal position inside the picture, 0 (left) to 1 (right)."
    )
    y: float = Field(
        ge=0, le=1, description="Vertical position inside the picture, 0 (top) to 1 (bottom)."
    )
    text: Text = Field(description="Callout text.")


class ScreenshotSlide(BaseModel):
    type: Literal["screenshot"] = Field(
        default="screenshot",
        description=("Slide type discriminator. The value is always 'screenshot'."),
    )
    title: str = Field(description="Slide headline.")
    image: Text = Field(
        description="Image file path or URL. A missing file renders a labelled placeholder."
    )
    callouts: list[Callout] = Field(default=[], max_length=8, description="Callouts, at most 8.")


class FigureSlide(BaseModel):
    type: Literal["figure"] = Field(
        default="figure", description="Slide type discriminator. The value is always 'figure'."
    )
    title: str = Field(description="Slide headline.")
    image: Text = Field(
        description="Image file path or URL. A missing file renders a labelled placeholder."
    )
    caption: Text | None = Field(default=None, description="Figure caption.")
    source: Text | None = Field(default=None, description="Optional source line.")
    bleed: bool = Field(
        default=False,
        description=(
            "If true, the picture fills the whole slide and the title sits in a dark band at the "
            "bottom, with the caption below it. The source is not shown."
        ),
    )
