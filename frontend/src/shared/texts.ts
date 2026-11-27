/** User-facing text of the shared layer. Each string lives here. */
export const SHARED_TEXTS = {
  loading: "Loading",
  retry: "Try again",
  cancel: "Cancel",
  error: {
    title: "Something went wrong",
    unknown: "The request failed. Try again in a moment.",
    network: "The server is not reachable. Check your connection and try again.",
    byCode: {
      ProjectNotFoundError: "This project does not exist anymore.",
      TurnInProgressError: "The assistant is still working on the last message.",
      PlanLockedError: "The plan is approved already. Ask for changes in the chat.",
      PlanMissingError: "There is no plan to approve yet.",
      PlanIncompleteError: "The plan is not complete yet. Answer the open questions first.",
      ToolCallNotFoundError: "This value is not available anymore.",
      ToolFieldNotFoundError: "This value is not available anymore.",
    } as Readonly<Record<string, string>>,
  },
} as const;
