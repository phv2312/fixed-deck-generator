import { useQuery, useQueryClient, type QueryClient } from "@tanstack/react-query";

import { getChat, getToolField } from "@/features/chat/api";
import type { ChatHistory } from "@/features/chat/types";

const POLL_MS = 2000;

export const chatKeys = {
  history: (projectId: string) => ["chat", projectId, "history"] as const,
  field: (url: string) => ["chat", "field", url] as const,
};

/** The chat history. It polls while a turn runs that this tab did not start. */
export function useChat(projectId: string): ReturnType<typeof useQuery<ChatHistory>> {
  return useQuery({
    queryKey: chatKeys.history(projectId),
    queryFn: ({ signal }) => getChat(projectId, signal),
    refetchInterval: (query) => (query.state.data?.running ? POLL_MS : false),
  });
}

/** The full value of one tool field. It loads only when `enabled` is true. */
export function useToolField(url: string, enabled: boolean): ReturnType<typeof useQuery<string>> {
  return useQuery({
    queryKey: chatKeys.field(url),
    queryFn: ({ signal }) => getToolField(url, signal),
    enabled,
    staleTime: Infinity,
  });
}

export function refreshChat(client: QueryClient, projectId: string): Promise<void> {
  return client.invalidateQueries({ queryKey: chatKeys.history(projectId) });
}

/** Return a function that copies the full value of a tool field to the clipboard. */
export function useCopyField(): (url: string) => Promise<void> {
  const client = useQueryClient();
  return async (url) => {
    const text = await client.fetchQuery({
      queryKey: chatKeys.field(url),
      queryFn: ({ signal }) => getToolField(url, signal),
      staleTime: Infinity,
    });
    await navigator.clipboard.writeText(text);
  };
}
