from typing import ClassVar

from decks.api.openapi import RouteDoc


class DeckDocs:
    """Swagger text of the deck endpoints."""

    READ: ClassVar[RouteDoc] = RouteDoc(
        "Read the deck",
        "Return every slide with its elements: id, type, box in canvas units, render order, "
        "the fields, and the names of the fields that an edit may change. Draw selection boxes "
        "from the box. The slide HTML of each element has the same id in `data-element-id`.",
    )
    SLIDE_HTML: ClassVar[RouteDoc] = RouteDoc(
        "Read a slide as HTML",
        "Return a self-contained HTML page that shows one slide of the built deck. The page "
        "scales to the width of its frame, so it fits in an `iframe`. The response has an "
        "`ETag` that is the `revision` of the slide in the deck response. Send it back in "
        "`If-None-Match` and the server answers 304 without a body when the slide has not "
        "changed. The `rev` query parameter only keeps the URL of a changed slide new; the "
        "server does not read it.",
    )
    UPDATE: ClassVar[RouteDoc] = RouteDoc(
        "Change an element",
        "Change fields of one element, such as its box, its text, or its style. The change is "
        "saved at once. A chat turn in progress blocks the edit. Editable fields by type: "
        "text: x, y, w, h, text, font_size, bold, italic, underline, color, font_family, align, "
        "valign, mono. shape: x, y, w, h, shape, fill, stroke, stroke_width, opacity, dash, "
        "radius. image: x, y, w, h, src, fit. table: x, y, w, h, rows, header, font_size. "
        "chart: x, y, w, h, kind, data. An image source must be an http(s) URL or a data:image "
        "URI.",
    )
    CREATE: ClassVar[RouteDoc] = RouteDoc(
        "Add an element",
        "Add a text, image, table, shape, or chart on top of a slide. Fields in `props` replace "
        "the defaults. An image needs `src`.",
    )
    DELETE: ClassVar[RouteDoc] = RouteDoc(
        "Delete an element",
        "Remove one element, also from inside a group. The deck can be undone.",
    )
    DUPLICATE: ClassVar[RouteDoc] = RouteDoc(
        "Duplicate an element",
        "Copy a top-level element. The copy sits 16 units down and to the right, above the "
        "original. A group cannot be duplicated.",
    )
    ORDER: ClassVar[RouteDoc] = RouteDoc(
        "Change the stacking order",
        "Move a top-level element one step up or down, or to the top or the bottom.",
    )
    UNDO: ClassVar[RouteDoc] = RouteDoc(
        "Undo the last edit",
        "Return the deck to how it was before the last edit. The revision still grows, so a "
        "client sees that the deck changed. At most 20 steps are kept.",
    )
    REDO: ClassVar[RouteDoc] = RouteDoc(
        "Redo an undone edit",
        "Bring back the deck that the last undo removed. A new edit clears the redo steps.",
    )
