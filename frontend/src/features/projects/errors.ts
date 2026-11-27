import { ApiError } from "@/shared/api";

/** A missing project cannot be fixed by a retry. */
export function isProjectNotFound(error: unknown): boolean {
  return error instanceof ApiError && error.code === "ProjectNotFoundError";
}
