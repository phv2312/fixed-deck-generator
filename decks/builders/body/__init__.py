"""family=body: Text, table, key-figure and terminal slides."""

from decks.builders.base import BaseBuilder

from .fromto import FromToBuilder
from .glossary import GlossaryBuilder
from .keyfigures import KeyFiguresBuilder
from .panels import PanelsBuilder
from .rows import RowsBuilder
from .table import TableBuilder
from .terminal import TerminalBuilder

FAMILY = "body"
BUILDERS: list[type[BaseBuilder]] = [
    FromToBuilder,
    GlossaryBuilder,
    KeyFiguresBuilder,
    PanelsBuilder,
    RowsBuilder,
    TableBuilder,
    TerminalBuilder,
]
