import type { ToolStatus } from "@/features/chat/types";

interface ToolCounts {
  running: number;
  failed: number;
}

/** User-facing text of the chat feature. Each string lives here. */
export const CHAT_TEXTS = {
  panelLabel: "Chat",
  empty: { title: "Start the conversation", hint: "Describe the deck you want. The assistant asks what it needs." },
  composer: { label: "Message", send: "Send message", hint: "Enter sends. Shift and Enter add a line." },
  assistantWorking: "The assistant is working",
  unavailable: "This chat is not available. Go back to All decks and open a deck that exists.",
  turnFailed: "The last message failed. Send it again.",
  tools: {
    used: (count: number): string => `Used ${count} ${count === 1 ? "tool" : "tools"}`,
    using: "Using tools",
    summary: ({ running, failed }: ToolCounts): string => {
      const parts = [running > 0 ? `${running} running` : "", failed > 0 ? `${failed} failed` : ""].filter(Boolean);
      return parts.length > 0 ? parts.join(", ") : "All done";
    },
    status: { running: "Running", done: "Done", error: "Failed" } satisfies Record<ToolStatus, string>,
    noDetails: "No details for this call.",
  },
  field: {
    meta: (size: string, mime: string): string => `${size} · ${mime}`,
    showAll: "Show all",
    copy: "Copy",
    copied: "Copied",
    previewAlt: (key: string): string => `Preview of ${key}`,
  },
  viewer: {
    label: (title: string): string => `Full value of ${title}`,
    copy: "Copy",
    copied: "Copied",
    download: "Download",
    close: "Close",
    loading: "Loading the full value",
    source: "Source",
  },
} as const;
