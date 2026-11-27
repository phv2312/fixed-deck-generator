import { PROJECT_TEXTS } from "@/features/projects/texts";
import type { Project } from "@/features/projects/types";

/** The name to show. A deck without a name takes its first slide title from the server. */
export function projectTitle(project: Project): string {
  return project.name || PROJECT_TEXTS.untitled;
}
