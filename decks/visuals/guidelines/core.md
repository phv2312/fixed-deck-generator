## Rules for every picture
- Output one SVG through the tool `save_visual`. The picture fills the body of a slide. The slide
  has its own title and a one-line caption, so do not repeat them.
- The picture may carry its own words: labels, annotations, short notes and a few lines of
  narrative, when they help the reader understand it. Copy every formula, number and label of the
  request exactly. Never paraphrase or correct them.
- Use the exact `viewBox` and `size` from the request. Keep every element inside it, with a
  margin of 24 units.
- Flat style only: solid fills, no gradient, shadow, blur, filter or image.
- Colour only through token classes (`class="fill-accent"`, `class="stroke-grid"`). Never write
  `#hex`, `rgb()` or a colour name. Text takes a `fill-*` class too.
- Use at most two token families as colour for meaning, and keep `accent` for the one thing that
  matters most.
- Font size is 12 to 24 units. Never below 11. Use `font-weight` 400 or 500 only.
- Write labels in sentence case, in the language of the brief. Keep each label under 25
  characters. A note may use a few short lines of at most 60 characters each. Do not use emoji.
- No `<script>`, `<foreignObject>`, external link or `@import`.
- A text with `text-anchor="end"` grows to the left; a text with `middle` grows both ways. Leave
  room for it.
- When `save_visual` returns issues, fix every error and call it again. Do not explain.

## Tokens
{tokens}
