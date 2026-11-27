/** Smallest hit area of an overlay box, in screen units. A line has no height. */
export const MIN_BOX = 16;
export const NUDGE = 1;
export const NUDGE_BIG = 10;
export const SNAP_THRESHOLD = 6;
export const MIN_ELEMENT_SIZE = 16;
export const PAGE_STEP = 16;

/** Color tokens of a deck theme. See decks/models/theme.py. */
export const COLOR_TOKENS = ["text", "muted", "primary", "accent", "light", "ink", "tint", "grid", "bg"] as const;

/** Named text sizes. They follow the type scale of the deck (`TYPE` in `decks/design.py`). The names live in the texts file. */
export const FONT_SIZES = [
  { key: "display", size: 64 },
  { key: "title", size: 36 },
  { key: "heading", size: 28 },
  { key: "lead", size: 22 },
  { key: "body", size: 18 },
  { key: "caption", size: 14 },
] as const;

/** Sizes the user picks from. A value outside the list stays selectable while an element has it. */
export const SIZE_PRESETS = {
  stroke_width: [1, 2, 3, 4, 6, 8, 12],
  width: [1, 2, 3, 4, 6, 8, 12],
  radius: [0, 4, 8, 12, 16, 24, 32],
} as const satisfies Record<string, readonly number[]>;

export const STALE_CODE = "StaleDeckRevisionError";

export const NEW_ELEMENT_BOX = { x: 400, y: 280, w: 480, h: 160 } as const;
export const NEW_ELEMENT_DEFAULTS = {
  text: { ...NEW_ELEMENT_BOX, text: "New text", font_size: 32 },
  shape: { ...NEW_ELEMENT_BOX, shape: "rect", fill: "tint" },
  table: { ...NEW_ELEMENT_BOX, rows: [["Header", "Header"], ["Cell", "Cell"]] },
  chart: { ...NEW_ELEMENT_BOX, kind: "bar", data: {} },
  image: { ...NEW_ELEMENT_BOX, h: 270, w: 480 },
} as const;
