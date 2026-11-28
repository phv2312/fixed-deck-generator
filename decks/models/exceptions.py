"""Errors raised by the slide parameter models.

``ModelError`` derives from ``ValueError``. Pydantic turns a ``ValueError`` raised in a
validator into a ``ValidationError``, so bad input still fails validation.
"""

from dataclasses import dataclass, fields
from typing import ClassVar


@dataclass
class ModelError(ValueError):
    """Base class of model errors. Subclasses set ``TEMPLATE`` and typed fields."""

    TEMPLATE: ClassVar[str] = "model error"

    def __str__(self) -> str:
        return self.TEMPLATE.format(**{f.name: getattr(self, f.name) for f in fields(self)})


@dataclass
class OrgNeedsMembersError(ModelError):
    """Raised when an org chart has neither members nor groups."""

    TEMPLATE = "org: needs members or groups"


@dataclass
class PyramidRingLevelsError(ModelError):
    """Raised when a ring pyramid does not have 3 to 5 levels."""

    TEMPLATE = "pyramid: style rings needs between 3 and 5 levels, got {count}"
    count: int


@dataclass
class SwimlaneUnknownLaneError(ModelError):
    """Raised when a swimlane step names a lane that is not declared."""

    TEMPLATE = "swimlanes: step '{step}' uses unknown lane '{lane}'"
    step: str
    lane: str


@dataclass
class SwimlaneLinkOutOfRangeError(ModelError):
    """Raised when a swimlane link points outside the step list."""

    TEMPLATE = "swimlanes: link {source}->{target} outside steps 0..{last}"
    source: int
    target: int
    last: int


@dataclass
class ContactTooManyPeopleError(ModelError):
    """Raised when contact cards hold more than 6 people without text."""

    TEMPLATE = "contact: cards take at most 6 people, got {count}; add a text for a team grid"
    count: int


@dataclass
class FromToShapeError(ModelError):
    """Raised when a from-to list pair has unequal or out-of-range item counts."""

    TEMPLATE = "fromto: left and right need the same number (1-6) of items, got {left} and {right}"
    left: int
    right: int


@dataclass
class PanelsColumnsLimitError(ModelError):
    """Raised when the columns style has more than 4 panels."""

    TEMPLATE = "panels: style columns takes at most 4 panels, got {count}"
    count: int


@dataclass
class PanelsIconsMinimumError(ModelError):
    """Raised when the icons style has fewer than 2 panels."""

    TEMPLATE = "panels: style icons needs at least 2 panels, got {count}"
    count: int


@dataclass
class TableRowWidthError(ModelError):
    """Raised when a table row does not have one cell per header column."""

    TEMPLATE = "table: every row needs {columns} cells"
    columns: int


@dataclass
class TableAlignLengthError(ModelError):
    """Raised when the table align list does not match the header columns."""

    TEMPLATE = "table: align needs {columns} entries"
    columns: int


@dataclass
class GanttRangeError(ModelError):
    """Raised when a gantt row has a start or end outside the period range."""

    TEMPLATE = "gantt: '{name}' must satisfy 0 <= start <= end < {periods}"
    name: str
    periods: int


@dataclass
class EvaluationCriteriaMismatchError(ModelError):
    """Raised when the evaluation score rows do not match the criteria count."""

    TEMPLATE = "evaluation: scores needs one row per criterion, got {rows} rows for {criteria}"
    rows: int
    criteria: int


@dataclass
class EvaluationOptionMismatchError(ModelError):
    """Raised when an evaluation score row does not match the options count."""

    TEMPLATE = "evaluation: every scores row needs one cell per option, expected {options}"
    options: int


@dataclass
class RaciAssignmentCountError(ModelError):
    """Raised when a RACI activity does not have one assignment per role."""

    TEMPLATE = "raci: '{activity}' needs {roles} assignments"
    activity: str
    roles: int


@dataclass
class RaciInvalidAssignmentError(ModelError):
    """Raised when a RACI cell holds a value outside R, A, C, I."""

    TEMPLATE = "raci: '{activity}' has an assignment outside R/A/C/I"
    activity: str


@dataclass
class RaciAccountableCountError(ModelError):
    """Raised when a RACI activity does not have exactly one A."""

    TEMPLATE = "raci: '{activity}' needs exactly one A"
    activity: str


@dataclass
class MekkoColumnLengthError(ModelError):
    """Raised when a mekko column does not have one value per part."""

    TEMPLATE = "mekko: column '{column}' needs {expected} values"
    column: str
    expected: int


@dataclass
class ChartSeriesLengthError(ModelError):
    """Raised when a chart series does not have one value per category."""

    TEMPLATE = "chart: series '{series}' needs {expected} values"
    series: str
    expected: int


@dataclass
class TableListLengthError(ModelError):
    """Raised when a per-column list of a table element does not match the column count."""

    TEMPLATE = "table: {field} needs {columns} entries"
    field: str
    columns: int


@dataclass
class TableHighlightRangeError(ModelError):
    """Raised when the highlighted row or column of a table element does not exist."""

    TEMPLATE = "table: {field} {index} is outside 0..{last}"
    field: str
    index: int
    last: int
