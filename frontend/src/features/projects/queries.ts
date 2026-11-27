import { useMutation, useQuery, useQueryClient, type QueryClient } from "@tanstack/react-query";

import { createProject, deleteProject, getProject, listProjects, type ListParams } from "@/features/projects/api";
import type { Project, ProjectCreate, ProjectList } from "@/features/projects/types";

const projectKeys = {
  all: ["projects"] as const,
  list: (params: ListParams) => ["projects", "list", params] as const,
  detail: (projectId: string) => ["projects", "detail", projectId] as const,
};

export function useProject(projectId: string): ReturnType<typeof useQuery<Project>> {
  return useQuery({
    queryKey: projectKeys.detail(projectId),
    queryFn: ({ signal }) => getProject(projectId, signal),
  });
}

/** Refresh every cached project, for example after a chat turn changed the phase. */
export function invalidateProjects(client: QueryClient): Promise<void> {
  return client.invalidateQueries({ queryKey: projectKeys.all });
}

export function useProjects(params: ListParams): ReturnType<typeof useQuery<ProjectList>> {
  return useQuery({
    queryKey: projectKeys.list(params),
    queryFn: ({ signal }) => listProjects(params, signal),
  });
}

export function useCreateProject(): ReturnType<typeof useMutation<Project, Error, ProjectCreate>> {
  const client = useQueryClient();
  return useMutation({
    mutationFn: createProject,
    onSuccess: () => client.invalidateQueries({ queryKey: projectKeys.all }),
  });
}

export function useDeleteProject(): ReturnType<typeof useMutation<void, Error, string>> {
  const client = useQueryClient();
  return useMutation({
    mutationFn: deleteProject,
    onSuccess: () => client.invalidateQueries({ queryKey: projectKeys.all }),
  });
}
