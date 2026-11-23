[← Architecture](README.md)

# Deck generation

`DeckGenerator.generate()` works in this order:

1. It finds the drafts that changed. A hash of each draft says if a slide must be rebuilt.
2. It fills all changed drafts in parallel. For each draft, it asks an LLM agent for the spec of the draft's kind.
3. It builds the slide with the builder of that kind.
4. `LayoutFitter` shrinks overflowing text. `DeckChecker` checks the slide.
5. An `error` issue makes the generator fill the slide again, up to `MAX_FILL_ATTEMPTS` times. Each new attempt gets the issues as feedback. A validation error counts as an attempt.
6. When the attempts end, `SlideFallback` makes a `content` slide, and the report has a warning.
7. The generator saves the deck and the build state.

An unknown kind in a saved plan goes to `KIND_ALIASES` in `decks/agents/catalog.py`. An alias names the kind that replaced a removed kind. A kind that has no alias falls back to `content`.
