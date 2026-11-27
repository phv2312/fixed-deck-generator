import type { StreamEvent } from "@/features/chat/types";

const PLAN_EVENTS: ReadonlySet<StreamEvent["type"]> = new Set(["question", "plan_updated", "deck_ready", "done"]);
const DECK_EVENTS: ReadonlySet<StreamEvent["type"]> = new Set(["deck_ready", "done"]);

/** The plan and the project list may have changed. */
export function changesPlan(event: StreamEvent): boolean {
  return PLAN_EVENTS.has(event.type);
}

/** The deck may have changed: the assistant built or edited it. */
export function changesDeck(event: StreamEvent): boolean {
  return DECK_EVENTS.has(event.type);
}
