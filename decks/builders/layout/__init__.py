"""family=layout: Opening, divider, agenda, text and closing slides."""

from decks.builders.base import BaseBuilder

from .agenda import AgendaBuilder
from .chapter import ChapterBuilder
from .contact import ContactBuilder
from .content import ContentBuilder
from .statement import StatementBuilder
from .title import TitleBuilder

FAMILY = "layout"
BUILDERS: list[type[BaseBuilder]] = [
    AgendaBuilder,
    ChapterBuilder,
    ContactBuilder,
    ContentBuilder,
    StatementBuilder,
    TitleBuilder,
]
