import type { StreamEvent, ToolCall } from "@/features/chat/types";

export interface Progress {
  index: number;
  total: number;
}

/** What the tab knows about a turn that is running now. History does not have it yet. */
export interface LiveTurn {
  text: string;
  tools: ToolCall[];
  status: string | null;
  progress: Progress | null;
}

export interface TurnState {
  /** The user message of the turn, shown until the history has it. */
  pending: string | null;
  live: LiveTurn | null;
  errorCode: string | null;
}

export type TurnAction =
  | { type: "start"; message: string }
  | { type: "event"; event: StreamEvent }
  | { type: "fail"; code: string }
  | { type: "finish" };

export const INITIAL_TURN: TurnState = { pending: null, live: null, errorCode: null };

const EMPTY_LIVE: LiveTurn = { text: "", tools: [], status: null, progress: null };

function finishTool(tools: ToolCall[], name: string, ok: boolean): ToolCall[] {
  const at = tools.findLastIndex((tool) => tool.name === name && tool.status === "running");
  if (at < 0) return tools;
  return tools.map((tool, position) => (position === at ? { ...tool, status: ok ? "done" : "error" } : tool));
}

function startTool(tools: ToolCall[], name: string): ToolCall[] {
  const tool: ToolCall = { id: `live-${tools.length}`, name, summary: "", status: "running", duration_ms: null, fields: [] };
  return [...tools, tool];
}

function applyEvent(live: LiveTurn, event: StreamEvent): LiveTurn {
  switch (event.type) {
    case "token":
      return { ...live, text: live.text + event.text };
    case "status":
      return { ...live, status: event.message };
    case "tool_started":
      return { ...live, tools: startTool(live.tools, event.name) };
    case "tool_finished":
      return { ...live, tools: finishTool(live.tools, event.name, event.ok) };
    case "deck_progress":
      return { ...live, progress: { index: event.index, total: event.total } };
    default:
      return live;
  }
}

export function turnReducer(state: TurnState, action: TurnAction): TurnState {
  switch (action.type) {
    case "start":
      return { pending: action.message, live: EMPTY_LIVE, errorCode: null };
    case "event": {
      const live = applyEvent(state.live ?? EMPTY_LIVE, action.event);
      const errorCode = action.event.type === "error" ? action.event.code : state.errorCode;
      return { ...state, live, errorCode };
    }
    case "fail":
      return { ...state, errorCode: action.code };
    case "finish":
      return { ...state, pending: null, live: null };
  }
}
