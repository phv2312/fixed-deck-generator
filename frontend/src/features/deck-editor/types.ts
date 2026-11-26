export type ElementType = "text" | "shape" | "image" | "table" | "chart" | "polygon" | "line" | "group";
export type NewKind = "text" | "image" | "table" | "shape" | "chart";
export type OrderMove = "forward" | "backward" | "front" | "back";

export interface DeckElement {
  id: string;
  type: ElementType;
  parent_id: string | null;
  z: number;
  x: number;
  y: number;
  w: number;
  h: number;
  props: Record<string, unknown>;
  editable: string[];
}

export interface DeckSlide {
  index: number;
  id: string;
  kind: string;
  title: string | null;
  elements: DeckElement[];
}

export interface Deck {
  revision: number;
  width: number;
  height: number;
  slides: DeckSlide[];
  can_undo: boolean;
  can_redo: boolean;
}

export interface LayoutIssue {
  code: string;
  severity: "error" | "warning";
  element_id: string | null;
  message: string;
  suggestion: string;
}

export interface EditResult {
  revision: number;
  element: DeckElement | null;
  issues: LayoutIssue[];
  can_undo: boolean;
  can_redo: boolean;
}

/** One edit of the deck. The hook adds the base revision. */
export type EditOp =
  | { kind: "patch"; slide: number; elementId: string; changes: Record<string, unknown> }
  | { kind: "add"; slide: number; newKind: NewKind; props: Record<string, unknown> }
  | { kind: "remove"; slide: number; elementId: string }
  | { kind: "duplicate"; slide: number; elementId: string }
  | { kind: "order"; slide: number; elementId: string; move: OrderMove }
  | { kind: "undo" }
  | { kind: "redo" };
