/** User-facing text of the pages layer. Each string lives here. */
export const PAGE_TEXTS = {
  backToDecks: "All decks",
  rightPane: "Deck workspace",
  buildDeckMessage: "The plan is approved. Build the deck.",
  deck: {
    approved: { title: "Plan approved", hint: "The assistant builds the deck next. Follow it in the chat." },
    generating: { title: "Building the deck", progress: (index: number, total: number): string => `Slide ${index} of ${total}` },
    generated: { title: "The deck is ready", hint: "The editor for the slides comes next.", slides: (count: number): string => (count === 1 ? "1 slide built." : `${count} slides built.`) },
    working: "Starting the build",
  },
} as const;
