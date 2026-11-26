import { useCallback, useEffect, useState } from "react";

import { STALE_CODE } from "@/features/deck-editor/constants";
import { moveChanges } from "@/features/deck-editor/geometry";
import { useDeck, useEditDeck } from "@/features/deck-editor/queries";
import { EDITOR_TEXTS } from "@/features/deck-editor/texts";
import type { Deck, DeckElement, DeckSlide, EditOp, LayoutIssue, NewKind, OrderMove } from "@/features/deck-editor/types";
import { ApiError } from "@/shared/api";

function noticeFor(error: unknown): string {
  if (!(error instanceof ApiError)) return EDITOR_TEXTS.notice.failed;
  if (error.code === STALE_CODE) return EDITOR_TEXTS.notice.stale;
  if (error.code === "TurnInProgressError") return EDITOR_TEXTS.notice.busy;
  if (error.code === "InvalidElementChangeError") return EDITOR_TEXTS.notice.invalid;
  return EDITOR_TEXTS.notice.failed;
}

function isTyping(target: EventTarget | null): boolean {
  return target instanceof HTMLElement && ["INPUT", "TEXTAREA", "SELECT"].includes(target.tagName);
}

export interface DeckEditorState {
  deck: Deck | undefined;
  query: ReturnType<typeof useDeck>;
  slide: DeckSlide | undefined;
  slideIndex: number;
  selected: DeckElement | undefined;
  editingText: boolean;
  notice: string | null;
  issues: LayoutIssue[];
  saving: boolean;
  selectSlide: (index: number) => void;
  select: (id: string | null) => void;
  startTextEdit: () => void;
  stopTextEdit: () => void;
  dismissNotice: () => void;
  patch: (changes: Record<string, unknown>, elementId?: string) => void;
  nudge: (dx: number, dy: number) => void;
  remove: () => void;
  duplicate: () => void;
  order: (move: OrderMove) => void;
  add: (kind: NewKind, props: Record<string, unknown>) => void;
  undo: () => void;
  redo: () => void;
}

/** The state and the actions of the editor. Every edit saves at once. */
export function useDeckEditor(projectId: string): DeckEditorState {
  const query = useDeck(projectId);
  const { edit, isPending } = useEditDeck(projectId);
  const [slideIndex, setSlideIndex] = useState(0);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [editingText, setEditingText] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);
  const [issues, setIssues] = useState<LayoutIssue[]>([]);

  const deck = query.data;
  const slide = deck?.slides[slideIndex];
  const selected = slide?.elements.find((el) => el.id === selectedId);

  const run = useCallback(
    async (op: EditOp): Promise<void> => {
      try {
        const result = await edit(op);
        if (result) setIssues(result.issues);
        setNotice(null);
        if (op.kind === "remove") setSelectedId(null);
        if (op.kind === "add" && result?.element) setSelectedId(result.element.id);
        if (op.kind === "duplicate" && result?.element) setSelectedId(result.element.id);
      } catch (error) {
        setNotice(noticeFor(error));
      }
    },
    [edit],
  );

  const patch = (changes: Record<string, unknown>, elementId?: string): void => {
    const id = elementId ?? selectedId;
    if (id) void run({ kind: "patch", slide: slideIndex, elementId: id, changes });
  };
  const withSelected = (make: (id: string) => EditOp): void => {
    if (selectedId) void run(make(selectedId));
  };

  useEffect(() => {
    const onKey = (event: KeyboardEvent): void => {
      if (!(event.metaKey || event.ctrlKey) || event.key.toLowerCase() !== "z" || isTyping(event.target)) return;
      event.preventDefault();
      void run({ kind: event.shiftKey ? "redo" : "undo" });
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [run]);

  return {
    deck, query, slide, slideIndex, selected, editingText, notice, issues, saving: isPending,
    selectSlide: (index) => {
      setSlideIndex(index);
      setSelectedId(null);
      setEditingText(false);
      setIssues([]);
    },
    select: (id) => {
      setSelectedId(id);
      setEditingText(false);
    },
    startTextEdit: () => setEditingText(true),
    stopTextEdit: () => setEditingText(false),
    dismissNotice: () => setNotice(null),
    patch,
    nudge: (dx, dy) => {
      if (selected) patch(moveChanges(selected, dx, dy));
    },
    remove: () => withSelected((id) => ({ kind: "remove", slide: slideIndex, elementId: id })),
    duplicate: () => withSelected((id) => ({ kind: "duplicate", slide: slideIndex, elementId: id })),
    order: (move) => withSelected((id) => ({ kind: "order", slide: slideIndex, elementId: id, move })),
    add: (kind, props) => void run({ kind: "add", slide: slideIndex, newKind: kind, props }),
    undo: () => void run({ kind: "undo" }),
    redo: () => void run({ kind: "redo" }),
  };
}
