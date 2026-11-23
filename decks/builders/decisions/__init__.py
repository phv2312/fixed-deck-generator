"""family=decisions: Options, assessments and decisions."""

from decks.builders.base import BaseBuilder

from .decision import DecisionBuilder
from .evaluation import EvaluationBuilder
from .for_against import ForAgainstBuilder
from .options import OptionsBuilder
from .raci import RaciBuilder
from .scorecard import ScorecardBuilder
from .swot import SwotBuilder

FAMILY = "decisions"
BUILDERS: list[type[BaseBuilder]] = [
    DecisionBuilder,
    EvaluationBuilder,
    ForAgainstBuilder,
    OptionsBuilder,
    RaciBuilder,
    ScorecardBuilder,
    SwotBuilder,
]
