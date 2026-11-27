import { useQueryClient } from "@tanstack/react-query";
import { useEffect, useReducer, useRef } from "react";

import { sendMessage } from "@/features/chat/api";
import { refreshChat, useChat } from "@/features/chat/queries";
import type { StreamEvent } from "@/features/chat/types";
import { INITIAL_TURN, turnReducer, type TurnState } from "@/features/chat/turnReducer";
import { ApiError } from "@/shared/api";

export interface ChatTurn extends TurnState {
  /** True while a turn runs, in this tab or in another one. */
  busy: boolean;
  send: (message: string) => Promise<void>;
}

interface Options {
  projectId: string;
  /** Called for each event of a turn that this tab sent. */
  onEvent?: (event: StreamEvent) => void;
}

const UNKNOWN_CODE = "UnknownError";

function errorCodeOf(error: unknown): string {
  return error instanceof ApiError ? error.code : UNKNOWN_CODE;
}

/** Send chat messages and follow the turn that answers them. */
export function useChatTurn({ projectId, onEvent }: Options): ChatTurn {
  const client = useQueryClient();
  const history = useChat(projectId);
  const [state, dispatch] = useReducer(turnReducer, INITIAL_TURN);
  const abort = useRef<AbortController | null>(null);

  useEffect(() => () => abort.current?.abort(), []);

  const send = async (message: string): Promise<void> => {
    abort.current = new AbortController();
    dispatch({ type: "start", message });
    try {
      await sendMessage({
        projectId,
        message,
        signal: abort.current.signal,
        onEvent: (event) => {
          dispatch({ type: "event", event });
          onEvent?.(event);
        },
      });
    } catch (error) {
      if (!(error instanceof DOMException)) dispatch({ type: "fail", code: errorCodeOf(error) });
    } finally {
      await refreshChat(client, projectId);
      dispatch({ type: "finish" });
    }
  };

  const busy = state.live !== null || (history.data?.running ?? false);
  return { ...state, busy, send };
}
