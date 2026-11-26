import { useMutation, useQuery, useQueryClient, type QueryClient } from "@tanstack/react-query";

import { getDeck, sendEdit } from "@/features/deck-editor/api";
import type { Deck, DeckElement, EditOp, EditResult } from "@/features/deck-editor/types";
import { ApiError } from "@/shared/api";
import { STALE_CODE } from "@/features/deck-editor/constants";

const deckKey = (projectId: string): readonly unknown[] => ["deck-editor", projectId, "deck"];

export function useDeck(projectId: string): ReturnType<typeof useQuery<Deck>> {
  return useQuery({
    queryKey: deckKey(projectId),
    queryFn: ({ signal }) => getDeck(projectId, signal),
    refetchOnMount: "always",
  });
}

const GEOMETRY = ["x", "y", "w", "h"];

/** Apply the changes of a patch to the cached element at once, so a drag does not jump back. */
function applyPatch(deck: Deck, slide: number, elementId: string, changes: Record<string, unknown>): Deck {
  const patch = (el: DeckElement): DeckElement => {
    if (el.id !== elementId) return el;
    const top: Partial<DeckElement> = {};
    const noBox = el.type === "line" || el.type === "polygon";
    for (const key of GEOMETRY) {
      if (!noBox && typeof changes[key] === "number") Object.assign(top, { [key]: changes[key] });
    }
    return { ...el, ...top, props: { ...el.props, ...changes } };
  };
  return {
    ...deck,
    slides: deck.slides.map((s) => (s.index === slide ? { ...s, elements: s.elements.map(patch) } : s)),
  };
}

function replaceElement(deck: Deck, slide: number, element: DeckElement): Deck {
  const swap = (el: DeckElement): DeckElement => (el.id === element.id ? element : el);
  return {
    ...deck,
    slides: deck.slides.map((s) => (s.index === slide ? { ...s, elements: s.elements.map(swap) } : s)),
  };
}

function settle(client: QueryClient, projectId: string, op: EditOp, result: EditResult | undefined): void {
  const key = deckKey(projectId);
  const deck = client.getQueryData<Deck>(key);
  if (op.kind === "patch" && result?.element && deck) {
    const next = replaceElement(deck, op.slide, result.element);
    client.setQueryData<Deck>(key, {
      ...next,
      revision: result.revision,
      can_undo: result.can_undo,
      can_redo: result.can_redo,
    });
    return;
  }
  void client.invalidateQueries({ queryKey: key });
}

interface Context {
  previous: Deck | undefined;
}

/** One serial queue of edits. Each edit reads the newest revision when it starts. */
export function useEditDeck(projectId: string): {
  edit: (op: EditOp) => Promise<EditResult | undefined>;
  isPending: boolean;
} {
  const client = useQueryClient();
  const key = deckKey(projectId);
  const mutation = useMutation<EditResult | undefined, Error, EditOp, Context>({
    scope: { id: `deck-edit-${projectId}` },
    mutationFn: (op) => {
      const revision = client.getQueryData<Deck>(key)?.revision ?? 0;
      return sendEdit(projectId, op, revision);
    },
    onMutate: (op) => {
      const previous = client.getQueryData<Deck>(key);
      if (op.kind === "patch" && previous) {
        client.setQueryData<Deck>(key, applyPatch(previous, op.slide, op.elementId, op.changes));
      }
      return { previous };
    },
    onSuccess: (result, op) => settle(client, projectId, op, result),
    onError: (error, _op, context) => {
      if (context?.previous) client.setQueryData<Deck>(key, context.previous);
      if (error instanceof ApiError && error.code === STALE_CODE) {
        void client.invalidateQueries({ queryKey: key });
      }
    },
  });
  return { edit: (op) => mutation.mutateAsync(op), isPending: mutation.isPending };
}
