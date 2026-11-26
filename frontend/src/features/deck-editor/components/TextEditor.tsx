import Box from "@mui/material/Box";
import { useRef } from "react";

import { EDITOR_TEXTS } from "@/features/deck-editor/texts";
import type { DeckElement } from "@/features/deck-editor/types";

const focusOnMount = (node: HTMLTextAreaElement | null): void => {
  node?.focus();
};

interface TextEditorProps {
  element: DeckElement;
  scale: number;
  onCommit: (text: string) => void;
  onCancel: () => void;
}

/** A text box over the element. Enter saves, Shift+Enter adds a line, Escape cancels. */
export function TextEditor({ element, scale, onCommit, onCancel }: TextEditorProps): React.JSX.Element {
  const cancelled = useRef(false);
  const { props } = element;
  const size = typeof props.font_size === "number" ? props.font_size : 16;
  const align = typeof props.align === "string" ? props.align : "left";
  return (
    <Box
      component="textarea"
      ref={focusOnMount}
      aria-label={EDITOR_TEXTS.textEditor}
      defaultValue={typeof props.text === "string" ? props.text : ""}
      onFocus={(event: React.FocusEvent<HTMLTextAreaElement>) => event.currentTarget.select()}
      onBlur={(event: React.FocusEvent<HTMLTextAreaElement>) => {
        if (cancelled.current) onCancel();
        else onCommit(event.currentTarget.value);
      }}
      onKeyDown={(event: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (event.key === "Escape") {
          cancelled.current = true;
          event.currentTarget.blur();
        } else if (event.key === "Enter" && !event.shiftKey) {
          event.preventDefault();
          event.currentTarget.blur();
        }
      }}
      style={{
        left: element.x * scale, top: element.y * scale, width: element.w * scale, height: element.h * scale,
        fontSize: size * scale, fontWeight: props.bold === true ? 700 : 400,
        fontStyle: props.italic === true ? "italic" : "normal", textAlign: align as "left" | "center" | "right",
      }}
      sx={{
        position: "absolute", zIndex: 5, boxSizing: "border-box", resize: "none", p: 0, m: 0,
        fontFamily: "inherit", lineHeight: 1.2, color: "text.primary", bgcolor: "background.paper",
        border: 2, borderColor: "primary.main", borderRadius: 0, outline: "none",
      }}
    />
  );
}
