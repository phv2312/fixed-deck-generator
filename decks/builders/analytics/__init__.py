"""family=analytics: Charts and data-driven slides."""

from decks.builders.base import BaseBuilder

from .bubble import BubbleBuilder
from .exhibit import ExhibitBuilder
from .mekko import MekkoBuilder
from .twocharts import TwoChartsBuilder

FAMILY = "analytics"
BUILDERS: list[type[BaseBuilder]] = [
    BubbleBuilder,
    ExhibitBuilder,
    MekkoBuilder,
    TwoChartsBuilder,
]
