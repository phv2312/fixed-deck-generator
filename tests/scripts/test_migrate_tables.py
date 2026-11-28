import pytest

from decks.models.elements import Line, Shape, Table, Text
from decks.models.slides import Slide
from scripts.migrate_tables import TableMigrator

COL_X = [74.0, 400.0]  # cell x of the old builder: the column x plus 10


def cell(text: str, col: int, row: int, *, align: str = "left") -> Text:
    """Return one cell text as the old builder wrote it: 54 px rows from y=150."""
    return Text(x=COL_X[col], y=150 + 54 * row, w=300, h=54, text=text, align=align)  # ty: ignore[invalid-argument-type]


def flat_slide(*, highlight: bool = False, note: bool = True) -> Slide:
    """Return a table slide in the old flattened form: texts, lines and tint shapes."""
    els: list = [Text(x=64, y=40, w=1152, h=60, text="Scores", font_size=28)]
    if highlight:
        els.append(Shape(x=390, y=150, w=300, h=162, fill="tint"))  # column 1
        els.append(Shape(x=64, y=258, w=1152, h=54, fill="tint"))  # body row 1
    rows = [["Head", "Score"], ["CTC", "12"], ["RNN-T", "14"]]
    for r, row in enumerate(rows):
        els += [cell(text, c, r, align="right" if c else "left") for c, text in enumerate(row)]
        els.append(Line(x1=64, y1=204 + 54 * r, x2=1216, y2=204 + 54 * r))
    if note:
        els.append(Text(x=64, y=378, w=1152, h=28, text="Source: test", font_size=12))
    return Slide(id="p8", family="body", kind="table", elements=els)


def test_flat_table_becomes_one_table_element() -> None:
    """Test that the cells, the note and the alignment are read back and ids are renumbered."""
    result = TableMigrator().migrate(flat_slide(), 7)

    assert result.slide is not None
    title, table = result.slide.elements
    assert (title.id, table.id) == ("s8e1", "s8e2")
    assert isinstance(table, Table)
    assert table.rows == [["Head", "Score"], ["CTC", "12"], ["RNN-T", "14"]]
    assert table.align == ["left", "right"]
    assert table.caption == "Source: test"
    assert (table.highlight_row, table.highlight_col) == (None, None)


def test_highlight_shapes_become_highlight_indexes() -> None:
    """Test that the tint shapes under the cells give the highlighted row and column."""
    result = TableMigrator().migrate(flat_slide(highlight=True, note=False), 7)

    assert result.slide is not None
    table = result.slide.elements[1]
    assert isinstance(table, Table)
    assert (table.highlight_row, table.highlight_col) == (1, 1)
    assert table.caption is None


@pytest.mark.parametrize("kind", ["content", "table"])
def test_other_slides_stay_as_they_are(kind: str) -> None:
    """Test that a slide of another kind, or one that has a table element already, is skipped."""
    slide = Slide(id="p1", family="body", kind=kind, elements=[Text(x=0, y=0, w=1, h=1, text="x")])
    if kind == "table":
        slide = slide.model_copy(
            update={"elements": [Table(x=0, y=0, w=1, h=1, rows=[["a"], ["b"]])]}
        )

    assert TableMigrator().migrate(slide, 0).slide is None
