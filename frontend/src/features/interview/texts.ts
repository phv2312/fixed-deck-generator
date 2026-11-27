/** User-facing text of the interview feature. Each string lives here. */
export const INTERVIEW_TEXTS = {
  question: {
    heading: "The assistant has a question",
    other: "Something else",
    answer: "Your answer",
    send: "Send answer",
  },
  working: { title: "The assistant is working", hint: "The next question or the plan shows here when it is ready." },
  start: { title: "Tell the assistant about your deck", hint: "Describe the topic and the audience in the chat. The assistant asks what it still needs." },
  plan: {
    heading: "Review the plan",
    summary: (count: number): string => (count === 1 ? "1 slide planned." : `${count} slides planned.`),
    metaHeading: "What the assistant knows",
    slidesHeading: "Slides",
    theme: "Theme",
    noSummary: "No summary yet.",
    missing: (items: string[]): string => `Still open: ${items.join(", ")}.`,
    approve: "Approve plan",
    approving: "Approving plan",
    requestChanges: "Request changes",
    cancelChanges: "Cancel changes",
    changesLabel: "What should change?",
    sendChanges: "Send changes",
    approved: "Plan approved",
    kindUnknown: "Kind not chosen",
    waiting: "The assistant is working. You can answer when it is done.",
  },
} as const;
