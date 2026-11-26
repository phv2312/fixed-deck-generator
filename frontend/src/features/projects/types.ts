/** Build phases of a project. See docs/architecture/agent-layer.md. */
export type Phase = "draft" | "interviewing" | "review" | "approved" | "generating" | "generated";

export interface Project {
  id: string;
  name: string;
  phase: Phase;
  created_at: string;
  updated_at: string;
  slide_count: number;
  thumbnail_url: string | null;
}

export interface ProjectList {
  items: Project[];
  total: number;
}

export interface ProjectCreate {
  name: string;
}
