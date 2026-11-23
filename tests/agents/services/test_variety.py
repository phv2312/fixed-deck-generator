import pytest

from decks.agents.catalog import SlideCatalog
from decks.agents.services.variety import VarietyPolicy
from decks.models.plan import Plan, SlideDraft


def _plan(*kinds: str | None) -> Plan:
    slides = [
        SlideDraft(id=f"p{i}", kind=k, purpose="x", title=f"T{i}") for i, k in enumerate(kinds, 1)
    ]
    return Plan(slides=slides)


@pytest.fixture
def policy() -> VarietyPolicy:
    """Policy over the real catalog."""
    return VarietyPolicy(SlideCatalog())


@pytest.mark.parametrize(
    "kinds",
    [
        ("title", "pyramid", "funnel", "cycle", "contact"),
        ("title", "swot", "raci", "scorecard", "contact"),
    ],
)
def test_three_in_a_row_from_one_family(policy: VarietyPolicy, kinds: tuple[str, ...]) -> None:
    """Three slides of one family in a row break the rule; the last one is named."""
    found = policy.violations(_plan(*kinds), complete=False)
    assert [v.slide_id for v in found] == ["p4"]


@pytest.mark.parametrize(
    ("kinds", "slide_ids"),
    [
        (("title", "content", "content", "contact"), ["p3"]),
        (("title", "table", "table", "table", "contact"), ["p3", "p4"]),
    ],
)
def test_same_kind_twice_in_a_row(
    policy: VarietyPolicy, kinds: tuple[str, ...], slide_ids: list[str]
) -> None:
    """A slide with the same kind as the slide before it breaks the rule."""
    found = policy.violations(_plan(*kinds), complete=False)
    assert [v.slide_id for v in found if "share a kind" in v.message] == slide_ids


@pytest.mark.parametrize(
    "kinds",
    [
        ("title", "pyramid", "funnel", "content", "contact"),
        ("title", "pyramid", None, "cycle", "contact"),
    ],
)
def test_no_violation(policy: VarietyPolicy, kinds: tuple[str | None, ...]) -> None:
    """Two in a row, or a slide without a kind, break no rule."""
    assert policy.violations(_plan(*kinds), complete=True) == []


@pytest.mark.parametrize(
    ("kinds", "slide_ids"),
    [
        (("content", "table", "contact"), ["p1"]),
        (("title", "table", "content"), ["p3"]),
        (("content", "table", "content"), ["p1", "p3"]),
        (("title",), []),
    ],
)
def test_first_and_last_slide(
    policy: VarietyPolicy, kinds: tuple[str, ...], slide_ids: list[str]
) -> None:
    """A complete deck opens with title and closes with contact or statement."""
    found = policy.violations(_plan(*kinds), complete=True)
    assert [v.slide_id for v in found] == slide_ids


def test_ends_are_not_checked_while_the_plan_grows(policy: VarietyPolicy) -> None:
    """Without ``complete`` the first and last slide rules stay silent."""
    assert policy.violations(_plan("content", "table"), complete=False) == []


def _visual_ids(found: list) -> list[str]:
    return [v.slide_id for v in found if "visual slide" in v.message]


def test_long_deck_without_visual_gets_advice(policy: VarietyPolicy) -> None:
    """A deck of 6 slides with no picture kind and no image gets advice on the last slide."""
    kinds = ("title", "content", "swot", "raci", "content", "contact")
    assert _visual_ids(policy.violations(_plan(*kinds), complete=True)) == ["p6"]


@pytest.mark.parametrize(
    "kinds",
    [
        ("title", "content", "swot", "raci", "figure", "contact"),
        ("title", "content", "swot", "raci", "content", "pyramid"),
        ("title", "content", "swot", "raci", "contact"),
    ],
)
def test_visual_slide_or_short_deck_is_fine(policy: VarietyPolicy, kinds: tuple[str, ...]) -> None:
    """A picture or diagram kind, or a deck of fewer than 6 slides, gives no advice."""
    assert _visual_ids(policy.violations(_plan(*kinds), complete=True)) == []


def test_image_counts_as_visual(policy: VarietyPolicy) -> None:
    """A slide with content.image is a visual slide, whatever its kind."""
    kinds = ("title", "content", "swot", "raci", "content", "contact")
    plan = _plan(*kinds)
    slide = plan.slides[1]
    with_image = slide.model_copy(
        update={"content": slide.content.model_copy(update={"image": "assets/v1.png"})}
    )
    plan = plan.model_copy(update={"slides": [plan.slides[0], with_image, *plan.slides[2:]]})
    assert _visual_ids(policy.violations(plan, complete=True)) == []


def test_visual_rule_off_without_chrome() -> None:
    """When the visual tools are unavailable, the rule is silent."""
    policy = VarietyPolicy(SlideCatalog(), visuals_available=False)
    kinds = ("title", "content", "swot", "raci", "content", "contact")
    assert _visual_ids(policy.violations(_plan(*kinds), complete=True)) == []


def test_visual_rule_waits_for_complete_plan(policy: VarietyPolicy) -> None:
    """The rule needs the whole deck: not while the plan grows, and not with an unchosen kind."""
    kinds = ("title", "content", "swot", "raci", "content", "contact")
    assert _visual_ids(policy.violations(_plan(*kinds), complete=False)) == []
    unset = ("title", "content", "swot", None, "content", "contact")
    assert _visual_ids(policy.violations(_plan(*unset), complete=True)) == []


def _with_image(plan: Plan, index: int, image: str | None) -> Plan:
    slide = plan.slides[index]
    changed = slide.model_copy(
        update={"content": slide.content.model_copy(update={"image": image})}
    )
    slides = [*plan.slides[:index], changed, *plan.slides[index + 1 :]]
    return plan.model_copy(update={"slides": slides})


def test_kind_that_needs_an_image_without_one(policy: VarietyPolicy) -> None:
    """A figure slide with no content.image is flagged at once, even while the plan grows."""
    plan = _plan("title", "figure", "content")
    found = policy.violations(plan, complete=False)
    assert [v.slide_id for v in found] == ["p2"]
    assert "create_diagram" in found[0].message


def test_image_present_or_text_kind_is_fine(policy: VarietyPolicy) -> None:
    """A figure with an image, and a kind that needs no image, give no advice."""
    plan = _with_image(_plan("title", "figure", "content"), 1, "assets/v1.png")
    assert policy.violations(plan, complete=False) == []


def test_missing_image_advice_without_chrome() -> None:
    """Without the visual tools the advice says to choose another kind."""
    policy = VarietyPolicy(SlideCatalog(), visuals_available=False)
    found = policy.violations(_plan("title", "figure"), complete=False)
    assert "create_" not in found[0].message
    assert "without a picture" in found[0].message
