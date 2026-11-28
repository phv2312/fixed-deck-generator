import pytest

from decks.agents.services.checker import DeckChecker
from decks.agents.services.fitter import LayoutFitter
from decks.builders.body.table import TableBuilder
from decks.models.body import TableSlide
from decks.models.elements import Table, Text
from decks.models.exceptions import TableHighlightRangeError, TableListLengthError
from decks.models.slides import Slide
from decks.table_layout import TableLayout

LONG = "word " * 60


def make_table(**fields: object) -> Table:
    """Return a 3 by 2 table with a header, with ``fields`` changed."""
    base: dict[str, object] = {
        "x": 64,
        "y": 150,
        "w": 1152,
        "h": 162,
        "font_size": 18,
        "rows": [["Head", "Score"], ["CTC", "12"], ["RNN-T", "14"]],
    }
    return Table.model_validate({**base, **fields})


def make_slide(*elements: Table | Text) -> Slide:
    """Return a slide that holds ``elements``."""
    return Slide(id="s1", family="body", kind="table", elements=list(elements))


@pytest.mark.parametrize(
    ("fields", "error"),
    [
        ({"col_widths": [1.0]}, TableListLengthError),
        ({"align": ["left"]}, TableListLengthError),
        ({"highlight_row": 2}, TableHighlightRangeError),
        ({"highlight_col": 2}, TableHighlightRangeError),
        ({"highlight_row": -1}, TableHighlightRangeError),
    ],
)
def test_table_refuses_lists_and_highlights_that_do_not_fit(
    fields: dict[str, object], error: type[Exception]
) -> None:
    """Test that the table model rejects a list of the wrong size and a highlight outside it."""
    with pytest.raises(ValueError, match="table") as raised:
        make_table(**fields)
    assert isinstance(raised.value.errors()[0]["ctx"]["error"], error)  # ty: ignore[unresolved-attribute]


@pytest.mark.parametrize(
    "rows", [[], [[]], [["a"]] * 41, [["a"] * 13]], ids=["none", "no cell", "41 rows", "13 columns"]
)
def test_table_refuses_a_size_that_the_layout_cannot_handle(rows: list[list[str]]) -> None:
    """Test that a table with no cell, or one that is too big, fails validation."""
    with pytest.raises(ValueError, match="table: needs 1 to 40 rows"):
        Table(x=0, y=0, w=100, h=10, rows=rows)


@pytest.mark.parametrize(
    ("body_rows", "font"), [(1, 18), (8, 18), (9, 16), (12, 16), (13, 14), (16, 14)]
)
def test_font_step_follows_the_row_count(body_rows: int, font: float) -> None:
    """Test the three font steps of the builder: 18 up to 8 rows, 16 up to 12, then 14."""
    assert TableLayout.font_step(body_rows) == font


def test_builder_gives_a_new_table_the_layout_of_the_old_one() -> None:
    """Test that the builder keeps the old geometry: row height, widths, number alignment."""
    spec = TableSlide(
        title="T",
        header=["Head", "Score"],
        rows=[["CTC", "12"], ["RNN-T", "14"]],
        highlight_col=1,
        note="note",
    )

    _title, table = TableBuilder().build(spec)

    assert isinstance(table, Table)
    assert (table.x, table.y, table.w) == (64, 150, 1152)
    assert (table.row_height, table.h, table.font_size) == (54, 162, 18)
    assert table.align == ["left", "right"]
    assert table.highlight_col == 1
    assert table.rules == "lines"
    assert sum(table.col_widths or []) == pytest.approx(1)
    assert table.caption == "note"


def test_builder_drops_a_highlight_that_is_out_of_range() -> None:
    """Test that a highlight outside the table does not crash the builder."""
    spec = TableSlide(title="T", header=["A"], rows=[["1"]], highlight_row=4)

    table = TableBuilder().build(spec)[1]

    assert isinstance(table, Table)
    assert table.highlight_row is None


def test_relaid_keeps_a_font_size_that_a_person_chose() -> None:
    """Test that the layout only lowers the font size and never raises it."""
    assert TableLayout().relaid(make_table(font_size=12)).font_size == 12


def test_relaid_returns_uneven_rows_as_they_are() -> None:
    """Test that a table with uneven rows is not changed, so validation can refuse it."""
    table = make_table().model_copy(update={"rows": [["a", "b"], ["c"]]})

    assert TableLayout().relaid(table) is table


def test_overflow_names_the_cell_and_the_fitter_repairs_it() -> None:
    """Test that a long cell overflows its row and a smaller font makes it fit."""
    table = make_table(
        rows=[["Head", "Score"], [LONG[:90], "12"], ["RNN-T", "14"]], row_height=40, h=120
    )
    layout = TableLayout()

    before = layout.overflow(table)
    fitted = layout.fitted(table)

    assert [(c.row, c.col) for c in before] == [(1, 0)]
    assert fitted.font_size < table.font_size
    assert layout.overflow(fitted) == []


def test_checker_reports_table_cells_and_numbers() -> None:
    """Test that the checker looks inside a table: overflow and figures that are not in the plan."""
    table = make_table(rows=[["Head", "Score"], [LONG, "9999"], ["a", "b"]], row_height=40)

    issues = DeckChecker().check_slide(make_slide(table), None)

    assert [i.code for i in issues] == ["text_overflow"]
    assert issues[0].element_id == table.id


def test_fitter_lowers_the_font_of_an_overflowing_table() -> None:
    """Test that the fitter reaches the cells of a table, as it reaches a text."""
    table = make_table(rows=[["Head", "Score"], [LONG[:90], "12"], ["a", "b"]], row_height=40)

    fitted = LayoutFitter().fit(make_slide(table)).elements[0]

    assert isinstance(fitted, Table)
    assert fitted.font_size < 18
