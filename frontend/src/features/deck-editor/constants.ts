/** Canvas of the deck engine, in its own units. See decks/design.py. */
export const CANVAS_WIDTH = 1280;
export const CANVAS_HEIGHT = 720;

/** Smallest hit area of an overlay box, in screen units. A line has no height. */
export const MIN_BOX = 16;
export const NUDGE = 1;
export const NUDGE_BIG = 10;
export const SNAP_THRESHOLD = 6;
export const MIN_ELEMENT_SIZE = 16;
export const PAGE_STEP = 16;

/** Color tokens of a deck theme. See decks/models/theme.py. */
export const COLOR_TOKENS = ["text", "muted", "primary", "accent", "light", "ink", "tint", "grid", "bg"] as const;

export const STALE_CODE = "StaleDeckRevisionError";

export const NEW_ELEMENT_BOX = { x: 400, y: 280, w: 480, h: 160 } as const;
export const NEW_ELEMENT_DEFAULTS = {
  text: { ...NEW_ELEMENT_BOX, text: "New text", font_size: 32 },
  shape: { ...NEW_ELEMENT_BOX, shape: "rect", fill: "tint" },
  table: { ...NEW_ELEMENT_BOX, rows: [["Header", "Header"], ["Cell", "Cell"]] },
  chart: { ...NEW_ELEMENT_BOX, kind: "bar", data: {} },
  image: { ...NEW_ELEMENT_BOX, h: 270, w: 480 },
} as const;
