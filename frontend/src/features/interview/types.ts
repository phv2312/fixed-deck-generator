export interface Question {
  question: string;
  options: string[] | null;
  allow_multiple: boolean;
  free_text: boolean;
}

export interface PlanSlide {
  id: string;
  kind: string | null;
  purpose: string;
  title: string;
  summary: string;
  points: string[];
}

export interface Plan {
  phase: string;
  revision: number;
  approved: boolean;
  can_approve: boolean;
  theme: string;
  meta: Record<string, string>;
  slides: PlanSlide[];
  missing: string[];
  variety: string[];
  pending_question: Question | null;
}
