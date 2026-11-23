# Builder authoring

One class renders each slide type. The class inherits `BaseBuilder` from `decks/builders/base.py`. The class owns the registry key, the description for the LLM, the spec model that it uses, and the rendering logic.

## Contract

```python
from decks.builders.base import BaseBuilder

from decks.models.diagram import CycleSlide
from decks.models.elements import Element


class CycleBuilder(BaseBuilder[CycleSlide]):
    """Render a circular cycle of stages around a centre label."""

    TYPE = "cycle"
    DESCRIPTION = "Use for a repeating or circular process with 3-6 stages."
    SPEC = CycleSlide

    def build(self, spec: CycleSlide) -> list[Element]: ...
```

- `TYPE` is the slide key in `DeckSpec` and in the registry. It must be unique.
- `DESCRIPTION` tells a human or a model when to use this slide.
- `SPEC` is the pydantic model that validates the deck JSON.
- `build` returns positioned elements. It must not change the spec.
- `builder_schema()` returns the description and the spec JSON schema.
- Use absolute imports (`from decks.builders.base import ...`) or one-dot imports (`from .base import ...`). Ruff `TID252` and the contract test ban parent-relative imports (`from ..` / `from ...`).
- Add a `Field(description=...)` to each field of each spec model. Thus an LLM can generate correct parameters. The contract test examines nested schemas and fails on a field without a description.

## Adding a builder

1. Add the spec model in the file of its family in `decks/models/`, for example `decks/models/diagram.py`.
2. Create one module for each builder in the correct `decks/builders/<family>/` package.
3. Export the class from the family package:

   ```python
   BUILDERS: list[type[BaseBuilder]] = [CycleBuilder, ...]
   ```

   The root registry in `decks/builders/__init__.py` finds the classes through the `BUILDERS` list of each family. No other registration is necessary.
4. Add a minimum of one example slide in `examples/`.
5. Regenerate the catalog with `uv run python -m scripts.gen_catalog`.
6. Run the verification commands below. Regenerate the gallery.

## Story and layout helpers

- The shared primitives (`title_el`, `bullets`, `banner`, ...) are in `decks/builders/common.py`. Do not put feature logic in this module.
- Chart drawing is in `decks/builders/charts/renderer.py` (`ChartRenderer`). Use `render()` for the standard layout. Use `draw(x, y, w, h)` to scale the chart into a box.
- Text fitting for full-bleed layouts is in `decks/builders/layout/textfit.py`.

## Verification

```bash
uv run ruff check
uv run ruff format --check
uv run ty check
uv run pytest
uv run python -m decks review -o gallery.html
```

`gallery.html` is the surface for visual review. It renders each example slide in both themes.
