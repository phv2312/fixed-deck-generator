"""family=diagram: Process and concept diagrams."""

from decks.builders.base import BaseBuilder

from .cycle import CycleBuilder
from .driver_tree import DriverTreeBuilder
from .fishbone import FishboneBuilder
from .funnel import FunnelBuilder
from .layers import LayersBuilder
from .matrix import MatrixBuilder
from .org import OrgBuilder
from .pillars import PillarsBuilder
from .process import ProcessBuilder
from .pyramid import PyramidBuilder
from .swimlanes import SwimlanesBuilder
from .venn import VennBuilder

FAMILY = "diagram"
BUILDERS: list[type[BaseBuilder]] = [
    CycleBuilder,
    DriverTreeBuilder,
    FishboneBuilder,
    FunnelBuilder,
    LayersBuilder,
    MatrixBuilder,
    OrgBuilder,
    PillarsBuilder,
    ProcessBuilder,
    PyramidBuilder,
    SwimlanesBuilder,
    VennBuilder,
]
