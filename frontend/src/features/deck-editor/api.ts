import { apiRequest } from "@/shared/api";
import type { Deck, DeckSlide, EditOp, EditResult } from "@/features/deck-editor/types";

const base = (projectId: string): string => `/api/v1/projects/${projectId}/deck`;

export function getDeck(projectId: string, signal?: AbortSignal): Promise<Deck> {
  return apiRequest<Deck>(base(projectId), { signal });
}

/** URL of the HTML of one slide. A new revision makes the browser load the new version. */
export function slideHtmlUrl(projectId: string, index: number, revision: string | number): string {
  return `${base(projectId)}/slides/${index}/html?rev=${revision}`;
}

/** URL of one slide of a deck. It follows the revision of the slide, or of the deck when the API gives none. */
export function slideUrl(projectId: string, deck: Deck, slide: DeckSlide): string {
  return slideHtmlUrl(projectId, slide.index, slide.revision ?? deck.revision);
}

function elementPath(projectId: string, slide: number, elementId?: string): string {
  const root = `${base(projectId)}/slides/${slide}/elements`;
  return elementId ? `${root}/${encodeURIComponent(elementId)}` : root;
}

/** Send one edit with the base revision. */
export function sendEdit(projectId: string, op: EditOp, baseRevision: number): Promise<EditResult> {
  const base_revision = baseRevision;
  switch (op.kind) {
    case "patch":
      return apiRequest(elementPath(projectId, op.slide, op.elementId), {
        method: "PATCH",
        body: { base_revision, changes: op.changes },
      });
    case "add":
      return apiRequest(elementPath(projectId, op.slide), {
        method: "POST",
        body: { base_revision, kind: op.newKind, props: op.props },
      });
    case "remove":
      return apiRequest(elementPath(projectId, op.slide, op.elementId), {
        method: "DELETE",
        query: { base_revision },
      });
    case "duplicate":
      return apiRequest(`${elementPath(projectId, op.slide, op.elementId)}/duplicate`, {
        method: "POST",
        body: { base_revision },
      });
    case "order":
      return apiRequest(`${elementPath(projectId, op.slide, op.elementId)}/order`, {
        method: "POST",
        body: { base_revision, move: op.move },
      });
    case "undo":
      return apiRequest(`${base(projectId)}/undo`, { method: "POST" });
    case "redo":
      return apiRequest(`${base(projectId)}/redo`, { method: "POST" });
  }
}
