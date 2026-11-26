import type { Phase } from "@/features/projects/types";

/** User-facing text of the projects feature. Each string lives here. */
export const PROJECT_TEXTS = {
  title: "Your decks",
  count: (total: number): string => (total === 1 ? "1 deck" : `${total} decks`),
  newDeck: "New deck",
  empty: { title: "No decks yet", hint: "Create a deck and the assistant will ask what it needs." },
  create: { title: "New deck", nameLabel: "Deck name", submit: "Create deck", submitting: "Creating deck" },
  delete: {
    action: (name: string): string => `Delete deck ${name}`,
    confirm: "Delete deck",
    title: "Delete this deck?",
    body: (name: string): string => `The deck "${name}" and its chat will be removed. This cannot be undone.`,
    submitting: "Deleting deck",
  },
  slides: (count: number): string => (count === 1 ? "1 slide" : `${count} slides`),
  noSlides: "No slides yet",
  thumbnailTitle: (name: string): string => `First slide of ${name}`,
  noThumbnail: "No preview yet",
  working: "Assistant working",
  phase: {
    draft: "Draft",
    interviewing: "Needs your answer",
    review: "Plan to review",
    approved: "Plan approved",
    generating: "Generating",
    generated: "Ready",
  } satisfies Record<Phase, string>,
} as const;
