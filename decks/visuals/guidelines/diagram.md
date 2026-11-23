## Diagram
- Show the mechanism: boxes for things, arrows for relations. Every arrow has a direction.
- At most 4 boxes in a row. With more, make two rows or split the idea.
- A box holds a label of at most 3 words and, when needed, a sub-label of at most 5 words.
  Make the box wider than its text: about 9 units per character at font size 14.
- Boxes use `fill-tint` with `stroke-grid`; the key box uses `fill-accent` with text `fill-bg`.
- Arrows are lines with a marker defined in `<defs>`. The marker uses `fill-muted`. Do not let
  an arrow cross a box or a text.
- Keep at least 24 units between boxes in a row, and 32 between rows.
- Read order is left to right, then top to bottom.
