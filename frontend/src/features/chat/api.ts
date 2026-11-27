import { apiRequest, apiText, streamRequest } from "@/shared/api";
import type { ChatHistory, StreamEvent } from "@/features/chat/types";

const projectPath = (projectId: string): string => `/api/v1/projects/${projectId}`;

export function getChat(projectId: string, signal?: AbortSignal): Promise<ChatHistory> {
  return apiRequest<ChatHistory>(`${projectPath(projectId)}/chat`, { signal });
}

/** Read the full value of a tool field. `url` is the path that the history gives. */
export function getToolField(url: string, signal?: AbortSignal): Promise<string> {
  return apiText(url, { signal });
}

export interface SendOptions {
  projectId: string;
  message: string;
  signal?: AbortSignal;
  onEvent: (event: StreamEvent) => void;
}

/** Send one chat message and read the events of the turn. */
export function sendMessage({ projectId, message, signal, onEvent }: SendOptions): Promise<void> {
  return streamRequest<StreamEvent>(`${projectPath(projectId)}/chat`, {
    body: { message },
    signal,
    onEvent,
  });
}
