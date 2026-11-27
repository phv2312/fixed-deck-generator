import Box from "@mui/material/Box";

import { MIN_BOX, NUDGE, NUDGE_BIG } from "@/features/deck-editor/constants";
import type { DeckEditorState } from "@/features/deck-editor/hooks/useDeckEditor";
import { EDITOR_TEXTS } from "@/features/deck-editor/texts";
import type { DeckElement } from "@/features/deck-editor/types";

const ARROWS: Record<string, [number, number]> = {
  ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, -1], ArrowDown: [0, 1],
};

function handleKey(event: React.KeyboardEvent, editor: DeckEditorState): void {
  const arrow = ARROWS[event.key];
  const step = event.shiftKey ? NUDGE_BIG : NUDGE;
  if (arrow) {
    event.preventDefault();
    editor.nudge(arrow[0] * step, arrow[1] * step);
  } else if (event.key === "Delete" || event.key === "Backspace") {
    event.preventDefault();
    editor.remove();
  } else if (event.key === "Escape") {
    editor.select(null);
  } else if (event.key === "Enter" && editor.selected?.type === "text") {
    event.preventDefault();
    editor.startTextEdit();
  }
}

function labelOf(element: DeckElement): string {
  const type = EDITOR_TEXTS.types[element.type] ?? element.type;
  const text = typeof element.props.text === "string" ? element.props.text.trim().slice(0, 40) : "";
  return text ? `${type}: ${text}` : EDITOR_TEXTS.elementLabel(type, element.id);
}

function boxStyle(element: DeckElement, scale: number): React.CSSProperties {
  const width = Math.max(element.w * scale, MIN_BOX);
  const height = Math.max(element.h * scale, MIN_BOX);
  return {
    left: element.x * scale - (width - element.w * scale) / 2,
    top: element.y * scale - (height - element.h * scale) / 2,
    width,
    height,
    zIndex: element.z + 1,
  };
}

interface ElementBoxesProps {
  elements: DeckElement[];
  scale: number;
  editor: DeckEditorState;
  onSelectedNode: (node: HTMLElement | null) => void;
  frozen: boolean;
}

/** One transparent button per element. It shows the hover rectangle and takes the click. */
export function ElementBoxes({ elements, scale, editor, onSelectedNode, frozen }: ElementBoxesProps): React.JSX.Element {
  return (
    <>
      {elements
        .filter((element) => element.type !== "group")
        .map((element) => {
          const selected = element.id === editor.selected?.id;
          return (
            <Box
              key={element.id}
              component="button"
              type="button"
              ref={selected ? onSelectedNode : undefined}
              data-deck-box=""
              data-selected={selected ? "" : undefined}
              aria-label={labelOf(element)}
              aria-pressed={selected}
              style={boxStyle(element, scale)}
              onClick={() => editor.select(element.id)}
              onDoubleClick={() => {
                if (element.type === "text" && element.editable.includes("text")) {
                  editor.select(element.id);
                  editor.startTextEdit();
                }
              }}
              onKeyDown={(event: React.KeyboardEvent) => selected && handleKey(event, editor)}
              sx={{
                position: "absolute", pointerEvents: frozen ? "none" : "auto", p: 0, m: 0, bgcolor: "transparent", cursor: "pointer",
                border: 1, borderColor: selected ? "primary.main" : "transparent",
                "&:hover": { borderColor: "primary.main" },
                "&:focus-visible": { borderColor: "primary.main", boxShadow: 2 },
              }}
            />
          );
        })}
    </>
  );
}
