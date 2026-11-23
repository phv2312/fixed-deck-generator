from decks.agents.catalog import SlideCatalog
from decks.agents.models import VarietyViolation
from decks.models.plan import Plan

MAX_FAMILY_RUN = 2  # slides in a row from one family
OPENING_KIND = "title"
CLOSING_KINDS = ("contact", "statement")

MIN_SLIDES_FOR_VISUAL = 6  # a deck this long should have at least one visual slide
VISUAL_FAMILIES = frozenset({"diagram", "analytics", "pictures"})


class VarietyPolicy:
    """Check the slide kinds of a plan against ``docs/rules/slide-variety.md``.

    A violation is advice. It never blocks the plan.
    """

    def __init__(self, catalog: SlideCatalog, *, visuals_available: bool = True) -> None:
        self._catalog = catalog
        self._visuals_available = visuals_available

    def violations(self, plan: Plan, *, complete: bool) -> list[VarietyViolation]:
        """Return the broken rules.

        The rules on repeated kinds and on families hold for every part of a plan, so they are
        always checked. The first and last slide rules and the visual rule need the whole deck, so
        they are checked only when ``complete`` is true.
        """
        found = [
            *self._repeated_kinds(plan),
            *self._family_runs(plan),
            *self._missing_images(plan),
        ]
        if complete:
            found.extend(self._ends(plan))
            found.extend(self._visual(plan))
        return found

    def _missing_images(self, plan: Plan) -> list[VarietyViolation]:
        """Flag a slide whose kind needs an image but has none. Any part of a plan can break it."""
        found: list[VarietyViolation] = []
        for slide in plan.slides:
            if slide.kind is None or slide.kind not in self._catalog:
                continue
            if "image" not in self._catalog.required_fields(slide.kind) or slide.content.image:
                continue
            fix = (
                "call create_diagram with real content and set content.image to the "
                "returned path, or choose a kind without a picture"
                if self._visuals_available
                else "choose a kind without a picture"
            )
            found.append(
                VarietyViolation(
                    slide_id=slide.id,
                    message=(
                        f"slide {slide.id} has kind {slide.kind}, which needs content.image; {fix}"
                    ),
                )
            )
        return found

    def _is_visual(self, kind: str | None, image: str | None) -> bool:
        if image:
            return True
        return kind is not None and self._catalog.family_of(kind) in VISUAL_FAMILIES

    def _visual(self, plan: Plan) -> list[VarietyViolation]:
        """Advise a picture when a long deck has none. Silent when the tools are unavailable."""
        if not self._visuals_available or len(plan.slides) < MIN_SLIDES_FOR_VISUAL:
            return []
        if any(s.kind is None for s in plan.slides):
            return []
        if any(self._is_visual(s.kind, s.content.image) for s in plan.slides):
            return []
        return [
            VarietyViolation(
                slide_id=plan.slides[-1].id,
                message=(
                    f"the deck has {len(plan.slides)} slides and no visual slide; where a slide "
                    "has a flow or a structure, consider create_diagram. Do not draw "
                    "a picture without real content"
                ),
            )
        ]

    def _repeated_kinds(self, plan: Plan) -> list[VarietyViolation]:
        """Flag a slide that has the same kind as the slide before it."""
        return [
            VarietyViolation(
                slide_id=current.id,
                message=(
                    f"slides {previous.id} and {current.id} both have kind {current.kind}; "
                    "two slides in a row must not share a kind"
                ),
            )
            for previous, current in zip(plan.slides, plan.slides[1:], strict=False)
            if current.kind is not None and current.kind == previous.kind
        ]

    def _family_runs(self, plan: Plan) -> list[VarietyViolation]:
        found: list[VarietyViolation] = []
        size = MAX_FAMILY_RUN + 1
        for start in range(len(plan.slides) - size + 1):
            window = plan.slides[start : start + size]
            if any(s.kind is None for s in window):
                continue
            families = {self._catalog.family_of(s.kind) for s in window if s.kind}
            if len(families) == 1:
                found.append(
                    VarietyViolation(
                        slide_id=window[-1].id,
                        message=(
                            f"slides {', '.join(s.id for s in window)} all use the family "
                            f"{families.pop()}; at most {MAX_FAMILY_RUN} in a row are allowed"
                        ),
                    )
                )
        return found

    def _ends(self, plan: Plan) -> list[VarietyViolation]:
        found: list[VarietyViolation] = []
        first, last = plan.slides[0], plan.slides[-1]
        if first.kind != OPENING_KIND:
            found.append(
                VarietyViolation(
                    slide_id=first.id, message=f"the first slide must have kind {OPENING_KIND}"
                )
            )
        if len(plan.slides) > 1 and last.kind not in CLOSING_KINDS:
            found.append(
                VarietyViolation(
                    slide_id=last.id,
                    message=(
                        f"the last slide must have one of the kinds {', '.join(CLOSING_KINDS)}; "
                        "add a closing slide or change the kind of this one"
                    ),
                )
            )
        return found
