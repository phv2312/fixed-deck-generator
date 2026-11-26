import type { DeckElement } from "@/features/deck-editor/types";

const round = (value: number): number => Math.round(value * 10) / 10;

export interface Box {
  x: number;
  y: number;
  w: number;
  h: number;
}

/** True when the element can be moved with `x` and `y`, or with its own points. */
export function canMove(element: DeckElement): boolean {
  const { editable, type } = element;
  if (type === "line") return editable.includes("x1");
  if (type === "polygon") return editable.includes("points");
  if (type === "group") return false;
  return editable.includes("x") && editable.includes("y");
}

/** True when the element can be resized by its handles. */
export function canResize(element: DeckElement): boolean {
  if (element.type === "line" || element.type === "polygon" || element.type === "group") return false;
  return ["x", "y", "w", "h"].every((field) => element.editable.includes(field));
}

function asPoints(value: unknown): [number, number][] {
  return Array.isArray(value) ? (value as [number, number][]) : [];
}

function num(value: unknown): number {
  return typeof value === "number" ? value : 0;
}

/** The changes that move an element by dx and dy canvas units. */
export function moveChanges(element: DeckElement, dx: number, dy: number): Record<string, unknown> {
  const { props } = element;
  if (element.type === "line") {
    return {
      x1: round(num(props.x1) + dx),
      y1: round(num(props.y1) + dy),
      x2: round(num(props.x2) + dx),
      y2: round(num(props.y2) + dy),
    };
  }
  if (element.type === "polygon") {
    return { points: asPoints(props.points).map(([x, y]) => [round(x + dx), round(y + dy)]) };
  }
  return { x: round(element.x + dx), y: round(element.y + dy) };
}

export function boxChanges(box: Box): Record<string, unknown> {
  return { x: round(box.x), y: round(box.y), w: round(box.w), h: round(box.h) };
}
