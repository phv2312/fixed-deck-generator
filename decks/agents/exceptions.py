from dataclasses import dataclass
from http import HTTPStatus

from decks.exceptions import AppError


@dataclass
class AgentsError(AppError):
    """Base class of every agent-layer error. Subclasses set ``TEMPLATE`` and typed fields."""

    TEMPLATE = "agent layer error"


@dataclass
class PlanError(AgentsError):
    """Base class of plan errors."""


@dataclass
class PlanMissingError(PlanError):
    """Raised when the project has no plan yet."""

    TEMPLATE = "the project has no plan yet"
    STATUS_CODE = HTTPStatus.CONFLICT


@dataclass
class PlanIncompleteError(PlanError):
    """Raised when the plan is incomplete, missing: …."""

    TEMPLATE = "the plan is incomplete, missing: {missing}"
    STATUS_CODE = HTTPStatus.CONFLICT
    missing: list[str]


@dataclass
class PlanNotApprovedError(PlanError):
    """Raised when the plan is not approved."""

    TEMPLATE = "the plan is not approved"


@dataclass
class SlideNotFoundError(PlanError):
    """Raised when slide … does not exist."""

    TEMPLATE = "slide {slide_id} does not exist"
    slide_id: str


@dataclass
class ElementNotFoundError(PlanError):
    """Raised when element … does not exist in slide …."""

    TEMPLATE = "element {element_id} does not exist in slide {slide_id}"
    slide_id: str
    element_id: str


@dataclass
class DeckError(AgentsError):
    """Base class of deck errors."""


@dataclass
class DeckMissingError(DeckError):
    """Raised when the project has no deck yet."""

    TEMPLATE = "the project has no deck yet"
    STATUS_CODE = HTTPStatus.NOT_FOUND


@dataclass
class GenerationInProgressError(DeckError):
    """Raised when a generation is already running for project …."""

    TEMPLATE = "a generation is already running for project {project_id}"
    STATUS_CODE = HTTPStatus.CONFLICT
    project_id: str


@dataclass
class RepairBudgetExceededError(DeckError):
    """Raised when no repair attempts remain for project …."""

    TEMPLATE = "no repair attempts remain for project {project_id}"
    project_id: str


@dataclass
class TurnInProgressError(DeckError):
    """Raised when a chat turn is already running for project {project_id}."""

    TEMPLATE = "a chat turn is already running for project {project_id}"
    STATUS_CODE = HTTPStatus.CONFLICT
    project_id: str


@dataclass
class UnsupportedKindError(DeckError):
    """Raised when slide kind … is not registered."""

    TEMPLATE = "slide kind {kind} is not registered"
    kind: str


@dataclass
class FillFailedError(DeckError):
    """Raised when could not fill slide … of kind …: …."""

    TEMPLATE = "could not fill slide {slide_id} of kind {kind}: {reason}"
    kind: str
    slide_id: str
    reason: str


@dataclass
class StyleNotSupportedError(DeckError):
    """Raised when element … of type … does not support …."""

    TEMPLATE = "element {element_id} of type {element_type} does not support {field}"
    element_id: str
    element_type: str
    field: str


@dataclass
class RepositoryError(AgentsError):
    """Base class of repository errors."""


@dataclass
class ProjectNotFoundError(RepositoryError):
    """Raised when project … does not exist."""

    TEMPLATE = "project {project_id} does not exist"
    STATUS_CODE = HTTPStatus.NOT_FOUND
    project_id: str


@dataclass
class ArtifactCorruptError(RepositoryError):
    """Raised when artifact … is not valid JSON for its model."""

    TEMPLATE = "artifact {path} is not valid JSON for its model"
    path: str


@dataclass
class InvalidThemeError(PlanError):
    """Raised when theme … is not available, use one of: …."""

    TEMPLATE = "theme {theme} is not available, use one of: {allowed}"
    theme: str
    allowed: list[str]


@dataclass
class MetaLengthMismatchError(PlanError):
    """Raised when set_meta gets lists of different length."""

    TEMPLATE = "set_meta got {keys} keys and {values} values; pass lists of equal length"
    keys: int
    values: int


@dataclass
class PlanMetaMissingError(PlanError):
    """Raised when slides are added before the required meta is set."""

    TEMPLATE = "set these meta keys before you add slides: {missing}"
    missing: list[str]


@dataclass
class NoSlidesError(PlanError):
    """Raised when final_check runs on a plan without slides."""

    TEMPLATE = "the plan has no slides; call add_plan_slides first"
