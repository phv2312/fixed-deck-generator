"""Turn the table slides that an older builder flattened into one native ``Table`` element.

An older table builder wrote each cell as a text and each rule as a line, so the editor could not
select the table. This script finds such a slide, reads the cells back, and builds the slide
again with the current builder. The default is a dry run. Use ``--write`` to save. The script
keeps the old deck in ``deck.json.bak`` first.

    uv run python -m scripts.migrate_tables projects/demo            # show what would change
    uv run python -m scripts.migrate_tables projects/demo --write    # save the change
"""

import argparse
import shutil
from dataclasses import dataclass
from pathlib import Path

from decks.agents.repos import ProjectRepositories
from decks.agents.services.checker import DeckChecker
from decks.agents.services.deck_editor import DeckEditor
from decks.builders.body.table import TableBuilder
from decks.design import BODY_TOP, CONTENT_W, TYPE
from decks.models.body import TableSlide
from decks.models.elements import Shape, Table, Text
from decks.models.slides import Slide


@dataclass(frozen=True)
class Migration:
    """The result for one slide: the new slide, or the reason that it stays as it is."""

    slide_id: str
    slide: Slide | None
    reason: str = ""


class TableMigrator:
    """Read a flattened table slide back into a ``TableSlide`` and build it again."""

    def __init__(self, builder: TableBuilder | None = None) -> None:
        self._builder = builder or TableBuilder()

    def migrate(self, slide: Slide, index: int) -> Migration:
        """Return the migration of ``slide``, which is the ``index``-th slide (from 0)."""
        if slide.kind != "table" or any(isinstance(e, Table) for e in slide.flat):
            return Migration(slide.id, None, "not a flattened table slide")
        spec = self._spec(slide)
        if spec is None:
            return Migration(slide.id, None, "the cells do not form a regular table")
        rebuilt = slide.model_copy(update={"elements": self._builder.build(spec)})
        return Migration(slide.id, rebuilt.numbered(index + 1))

    def _spec(self, slide: Slide) -> TableSlide | None:
        texts = [e for e in slide.flat if isinstance(e, Text)]
        if len(texts) < 3:
            return None
        title, cells = texts[0], texts[1:]
        note = None
        if cells[-1].font_size == TYPE["caption"]:
            note, cells = cells[-1].text, cells[:-1]
        columns = sum(1 for cell in cells if cell.y == cells[0].y)
        if columns == 0 or len(cells) % columns or len(cells) // columns < 2:
            return None
        header, body = cells[:columns], cells[columns:]
        rows = [[c.text for c in body[i : i + columns]] for i in range(0, len(body), columns)]
        row_height = header[0].h
        highlight_row, highlight_col = self._highlights(slide, header, row_height)
        return TableSlide(
            title=title.text,
            header=[c.text for c in header],
            rows=rows,
            align=[c.align for c in header],
            highlight_row=highlight_row,
            highlight_col=highlight_col,
            note=note,
        )

    def _highlights(
        self, slide: Slide, header: list[Text], row_height: float
    ) -> tuple[int | None, int | None]:
        """Read the highlighted row and column from the tint shapes under the cells."""
        row = col = None
        for shape in (e for e in slide.flat if isinstance(e, Shape) and e.fill == "tint"):
            if shape.w >= CONTENT_W - 1:
                row = round((shape.y - BODY_TOP) / row_height) - 1
            else:
                col = next(
                    (j for j, cell in enumerate(header) if abs(cell.x - 10 - shape.x) < 1), None
                )
        return row, col


def main() -> None:
    """Migrate the table slides of one project folder."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("project", type=Path, help="the project folder, for example projects/demo")
    parser.add_argument("--write", action="store_true", help="save the change (default: dry run)")
    args = parser.parse_args()

    repos = ProjectRepositories(args.project.parent).for_project(args.project.name)
    deck = repos.deck.load()
    if deck is None:
        parser.error("the project has no deck")
    migrator = TableMigrator()
    slides, changed = list(deck.slides), 0
    for index, slide in enumerate(deck.slides):
        result = migrator.migrate(slide, index)
        if result.slide is None:
            if slide.kind == "table":
                print(f"skip {result.slide_id}: {result.reason}")
            continue
        slides[index] = result.slide
        changed += 1
        print(f"{'migrate' if args.write else 'would migrate'} {result.slide_id}")
    if not (args.write and changed):
        return
    shutil.copy(args.project / "deck.json", args.project / "deck.json.bak")
    # A migration is not a manual edit, so no slide is marked as edited.
    DeckEditor(repos, DeckChecker()).commit(deck.model_copy(update={"slides": slides}))


if __name__ == "__main__":
    main()
