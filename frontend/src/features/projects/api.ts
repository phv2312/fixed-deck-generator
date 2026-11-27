import { apiRequest } from "@/shared/api";
import type { Project, ProjectCreate, ProjectList } from "@/features/projects/types";

const BASE = "/api/v1/projects";

export interface ListParams {
  limit: number;
  offset: number;
}

export function listProjects(params: ListParams, signal?: AbortSignal): Promise<ProjectList> {
  return apiRequest<ProjectList>(BASE, { query: { ...params }, signal });
}

export function getProject(projectId: string, signal?: AbortSignal): Promise<Project> {
  return apiRequest<Project>(`${BASE}/${projectId}`, { signal });
}

export function createProject(body: ProjectCreate): Promise<Project> {
  return apiRequest<Project>(BASE, { method: "POST", body });
}

export async function deleteProject(projectId: string): Promise<void> {
  await apiRequest<unknown>(`${BASE}/${projectId}`, { method: "DELETE" });
}
