import { useQueryClient } from "@tanstack/react-query";

import { changesDeck, changesPlan, useChatTurn, type ChatTurn } from "@/features/chat";
import { refreshDeck } from "@/features/deck-editor";
import { refreshPlan } from "@/features/interview";
import { invalidateProjects } from "@/features/projects";

/** The chat turn of a project. Each event that changes the plan or the deck refreshes the views of it. */
export function useProjectTurn(projectId: string): ChatTurn {
  const client = useQueryClient();
  return useChatTurn({
    projectId,
    onEvent: (event) => {
      if (changesPlan(event)) {
        void refreshPlan(client, projectId);
        void invalidateProjects(client);
      }
      if (changesDeck(event)) void refreshDeck(client, projectId);
    },
  });
}
