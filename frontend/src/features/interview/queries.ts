import { useMutation, useQuery, useQueryClient, type QueryClient } from "@tanstack/react-query";

import { approvePlan, getPlan } from "@/features/interview/api";
import type { Plan } from "@/features/interview/types";

const planKeys = {
  detail: (projectId: string) => ["plan", projectId] as const,
};

export function usePlan(projectId: string): ReturnType<typeof useQuery<Plan>> {
  return useQuery({
    queryKey: planKeys.detail(projectId),
    queryFn: ({ signal }) => getPlan(projectId, signal),
  });
}

/** Refresh the plan, for example after the assistant changed it. */
export function refreshPlan(client: QueryClient, projectId: string): Promise<void> {
  return client.invalidateQueries({ queryKey: planKeys.detail(projectId) });
}

export function useApprovePlan(projectId: string): ReturnType<typeof useMutation<void, Error, void>> {
  const client = useQueryClient();
  return useMutation({
    mutationFn: () => approvePlan(projectId),
    onSuccess: () => refreshPlan(client, projectId),
  });
}
