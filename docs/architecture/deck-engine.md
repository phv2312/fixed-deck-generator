[← Architecture](README.md)

# Deck engine

## Models

`decks/models/slides.py` defines `SlideSpec`. It is a union of all slide models. The `type` field is the discriminator. `DeckSpec` holds a theme and a list of `SlideSpec`.

A builder turns a slide spec into a list of `Element` (`decks/models/elements.py`). An element is a `Text`, `Shape`, `Line`, `Polygon`, `Image`, `Table`, `Chart` or `Group`. Each element has fixed coordinates on a 1280 by 720 canvas. A `Slide` holds the elements. A `Deck` holds the slides and the theme.

Every field of a slide model has a `Field(description=...)`. The LLM reads these descriptions as its parameter documentation.

## Builders and the registry

Each slide kind has one builder class. The class inherits `BaseBuilder` and defines `TYPE`, `DESCRIPTION`, `SPEC` and `build`.

The registry has 43 kinds in 7 families:

| Family | Use |
|---|---|
| `layout` | Opening, divider, agenda, text and closing slides. |
| `body` | Text, table, key-figure and terminal slides. |
| `analytics` | Charts and data slides. |
| `diagram` | Process and concept diagrams. |
| `decisions` | Options, assessments and decisions. |
| `programme` | Plans, timelines and project status. |
| `pictures` | Slides built around a picture. |

Each family package exports `FAMILY` and `BUILDERS`. `decks/builders/__init__.py` lists the family packages in `FAMILIES`. `Registry` builds each builder once. `REGISTRY[kind]` returns the builder and its family name. No other registration is necessary.

`build_deck(spec)` looks up the builder of each slide and collects the slides into a `Deck`.

A kind can have more than one look. A merged kind uses a field to choose the look. For example, `pyramid` has `style="rings"`, `panels` has `style="icons"` and `figure` has `bleed=true`.

## Layout rules

- Shared primitives (`title_el`, `bullets`, `banner`, and others) are in `decks/builders/common.py`. Do not put feature logic there.
- Design tokens are in `decks/design.py`. Use a type role (`TYPE["body"]`), not a number.
- `TextMetrics` estimates how much room a text needs. It is the only estimator. The builders, the checker and the fitter all use it.
- `TextMetrics.lines` counts the wrapped lines with word wrapping. `height` and `fit_font_size` use it.
- `TextMetrics.fit_font_size` returns a `Fit` (size and line count).
- `TextMetrics` is a heuristic, not a browser layout.
- Colors are theme tokens (`primary`, `accent`, `tint`, and others). A builder never writes a color value.

## Render

`decks/render/html.py` turns a `Deck` into one self-contained HTML file. Each slide is a `<section>` with `data-family` and `data-kind` attributes. `decks/render/gallery.py` builds the review gallery of every example in both themes.
