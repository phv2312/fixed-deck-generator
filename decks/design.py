"""Design tokens shared by every builder. Use these instead of ad hoc numbers.

Type scale (px on the 1280x720 canvas). Pick the role, not a number:
    caption 12   footnotes, sources, page-level fine print only
    small   14   secondary labels, table cells in dense tables
    body    16   default running text in cards and lists
    body_l  18   body text with room to spare
    lead    22   lead paragraphs, takeaways, statements inside a slide
    h3      28   panel and card headings, big list items
    h2      36   slide titles
    h1      48   opening / divider headlines
    display 64   a single hero sentence
    hero    96   one hero figure (use sparingly)
Sizes outside the scale are only allowed when text must shrink to fit; then use `snap_down`.

Corner radius: none (0) for rules and full-bleed blocks, sm (4) for small markers and chips,
md (8) for every card or panel, pill (999) for pills and badges. Nothing else.

Spacing is an 8 px grid: xs 8, s 16, m 24, l 32, xl 48. Slide margin 64, gutter 24.

Design rules every slide follows:
- One emphasis per slide: a single element carries the colour, size or fill; everything else stays
  quiet.
- Structure encodes information: numbers only on real sequences (steps, timelines, ranked rows,
  agenda chapters); rules, outlines and fills only where they group or rank content.
- No all-caps labels and no eyebrow label above a heading unless it names the data.
- Prefer whitespace and thin rules to a tinted card around everything; use a filled card to mark
  the one thing that matters (a recommendation, the current step, the highlighted item).
- A chart, diagram or table is the visual; do not add decoration next to it.
"""

TYPE = {
    "caption": 12,
    "small": 14,
    "body": 16,
    "body_l": 18,
    "lead": 22,
    "h3": 28,
    "h2": 36,
    "h1": 48,
    "display": 64,
    "hero": 96,
}
RADIUS = {"none": 0, "sm": 4, "md": 8, "pill": 999}
SPACE = {"xs": 8, "s": 16, "m": 24, "l": 32, "xl": 48}
W, H = 1280, 720  # slide canvas in px
MARGIN = 64
GUTTER = 24
CONTENT_W = W - 2 * MARGIN  # width between the slide margins
CONTENT_TOP = 140  # first y below the title
TITLE_Y, TITLE_H = 40, 60  # the title box
BANNER_Y, BANNER_H = 590, 56  # the takeaway banner at the foot of a slide

# Traffic-light status colours; the single source for trackers, scorecards and window chrome.
GREEN, AMBER, RED, GREY = "#2E9E5B", "#F5A623", "#D64545", "#9CA3AF"

# Text measurement shared by the fitter, the checker and the HTML renderer.
LINE_HEIGHT = 1.3
CHAR_WIDTH = 0.55  # average glyph width as a fraction of the font size
BOLD_CHAR_WIDTH = 0.5  # bold headlines measure narrower in the browser than the estimate
BOLD_CHAR_WIDTH_SAFE = 0.58  # conservative bold width used when wrapping must not under-count
MONO_FONT = "Menlo,Consolas,monospace"

_SIZES = sorted(TYPE.values())


def snap_down(size: float) -> int:
    """Largest scale size that is <= size (smallest size if below the scale)."""
    return max([s for s in _SIZES if s <= size] or [_SIZES[0]])
