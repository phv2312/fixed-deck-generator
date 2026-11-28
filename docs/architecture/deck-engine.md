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

## Tables

The `table` builder writes one `Table` element, not one text for each cell. A person can then select the whole table, and add or remove a row or a column.

- A `Table` has `rows` (the header is the first row when `header` is true), `font_size`, `col_widths` (fractions of `w`), `align` (one value for each column), `row_height`, `highlight_row`, `highlight_col`, `rules` and `caption`. Each field after `font_size` is optional. With no field set, the table keeps the plain grid look.
- `rules` `"lines"` draws a heavy rule under the header and a hairline under each row. `caption` is a note below the table. It is outside the box, so it follows the table when the table grows.
- `highlight_row` counts the rows below the header.
- The model refuses a table with no cell, one with more than 40 rows or 12 columns, uneven rows, a list that does not match the columns, and a highlight outside the table.
- `TableLayout` (`decks/table_layout.py`) is the only code that sizes a table. The builder, the deck API, the checker, the fitter and the `set_table` tool all use it. `relaid` sets the row height, the column widths, the alignment and the table height. It only lowers the font size. It drops a highlight that left the table. `adapted` calls `relaid` only when the number of rows or columns changes, so a change of cell text keeps the layout.
- The checker reports a cell that needs more height than its row (`text_overflow`) and checks the cell numbers against the plan. The fitter lowers the font size until each cell fits.
- Decks that an older builder made have a table slide of many texts and lines. They still render. Run `uv run python -m scripts.migrate_tables <project folder>` to change them. The script shows the change first. Add `--write` to save it. It keeps `deck.json.bak`.

## Render

A renderer turns a `Deck` into one output. Each backend is a subclass of `DeckRenderer[T]` in `decks/render/base.py`. The base class has one abstract method for each element type and one for a slide. Its `element` method sends each element to the method for its type. It raises `UnsupportedElementError` (`decks/render/exceptions.py`) for an unknown type.

`HtmlRenderer` in `decks/render/htmldoc/services.py` is the HTML backend. Its `document` method returns one self-contained HTML file. Each slide is a `<section>` with `data-family` and `data-kind` attributes. Each element has `data-element-id` with its id, so an editor can match the DOM to the model. The markup of each element type is a Jinja2 template in `decks/render/htmldoc/templates/`. A method of `HtmlRenderer` computes the values that the template needs and renders it. `HtmlPageStyle` holds the look values, such as the title, the font weights, and the dash patterns. Templates read them as `page`. Templates do not escape by default. Use the `esc` filter on each text value. Use the `g` filter on each number.

To add a backend, for example PPTX, make a subclass of `DeckRenderer[T]` in its own package under `decks/render/`. Do not put HTML code in the base class.

## Review gallery

`decks/render/services.py` builds the review gallery of every example in both themes. It makes view models in `decks/render/models.py`. It renders `decks/render/templates/gallery.html.j2` through `GalleryTemplates`. A template error raises `GalleryTemplateError` (`decks/render/exceptions.py`).

## Model errors

Each model error is a dataclass in `decks/models/exceptions.py`. Each class has a `TEMPLATE` string and typed fields. `ModelError` derives from `ValueError`. Pydantic turns a `ValueError` raised in a validator into a `ValidationError`, so bad input still fails validation.
