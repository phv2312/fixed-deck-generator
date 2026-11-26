import { apiRequest } from "@/shared/api";
import type { Plan } from "@/features/interview/types";

const planPath = (projectId: string): string => `/api/v1/projects/${projectId}/plan`;

export function getPlan(projectId: string, signal?: AbortSignal): Promise<Plan> {
  return apiRequest<Plan>(planPath(projectId), { signal });
}

export async function approvePlan(projectId: string): Promise<void> {
  await apiRequest<unknown>(`${planPath(projectId)}/approve`, { method: "POST" });
}
