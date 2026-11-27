export type ToolStatus = "running" | "done" | "error";

export interface ToolField {
  key: string;
  size: number;
  mime: string;
  preview: string;
  url: string;
}

export interface ToolCall {
  id: string;
  name: string;
  summary: string;
  status: ToolStatus;
  duration_ms: number | null;
  fields: ToolField[];
}

export interface Question {
  question: string;
  options: string[] | null;
  allow_multiple: boolean;
  free_text: boolean;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  text: string;
  tool_calls: ToolCall[];
  question: Question | null;
}

export interface ChatHistory {
  messages: ChatMessage[];
  running: boolean;
  pending_question: Question | null;
}

/** The events of a chat turn. See `StreamEvent` in docs/architecture/agent-layer.md. */
export type StreamEvent =
  | { type: "run_started"; agent: string; phase: string }
  | { type: "status"; message: string }
  | { type: "token"; text: string }
  | { type: "tool_started"; name: string }
  | { type: "tool_finished"; name: string; ok: boolean }
  | ({ type: "question" } & Question)
  | { type: "plan_updated"; revision: number; slide_count: number; missing: string[] }
  | { type: "deck_progress"; index: number; total: number; slide_id: string; kind: string }
  | { type: "deck_ready"; built: number; failed: string[]; warnings: string[] }
  | { type: "error"; code: string; message: string }
  | { type: "done" };
