"""family=programme: Plans, timelines and project status."""

from decks.builders.base import BaseBuilder

from .discussion import DiscussionBuilder
from .gantt import GanttBuilder
from .steps import StepsBuilder
from .timeline import TimelineBuilder
from .tracker import TrackerBuilder

FAMILY = "programme"
BUILDERS: list[type[BaseBuilder]] = [
    DiscussionBuilder,
    GanttBuilder,
    StepsBuilder,
    TimelineBuilder,
    TrackerBuilder,
]
