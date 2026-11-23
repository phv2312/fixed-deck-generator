"""family=pictures: Slides built around a picture."""

from decks.builders.base import BaseBuilder

from .figure import FigureBuilder
from .screenshot import ScreenshotBuilder

FAMILY = "pictures"
BUILDERS: list[type[BaseBuilder]] = [
    FigureBuilder,
    ScreenshotBuilder,
]
