import ContentCopy from "@mui/icons-material/ContentCopy";
import DeleteOutlined from "@mui/icons-material/DeleteOutlined";
import KeyboardArrowDown from "@mui/icons-material/KeyboardArrowDown";
import KeyboardArrowUp from "@mui/icons-material/KeyboardArrowUp";
import Divider from "@mui/material/Divider";
import IconButton from "@mui/material/IconButton";
import Paper from "@mui/material/Paper";
import { autoUpdate, flip, offset, shift, useFloating } from "@floating-ui/react";
import { useState } from "react";

import { TypeControls } from "@/features/deck-editor/components/toolbar/controls";
import { CellsDialog, DataDialog, ImageUrlDialog } from "@/features/deck-editor/components/toolbar/dialogs";
import type { DeckEditorState } from "@/features/deck-editor/hooks/useDeckEditor";
import { EDITOR_TEXTS } from "@/features/deck-editor/texts";
import type { DeckElement } from "@/features/deck-editor/types";

const T = EDITOR_TEXTS.toolbar;
const GAP = 8;

interface ElementToolbarProps {
  element: DeckElement;
  target: HTMLElement;
  editor: DeckEditorState;
  hidden: boolean;
  onModal: (open: boolean) => void;
}

function CommonControls({ element, editor }: { element: DeckElement; editor: DeckEditorState }): React.JSX.Element {
  const topLevel = element.parent_id === null;
  const actions = [
    { label: T.forward, icon: <KeyboardArrowUp fontSize="small" />, run: () => editor.order("forward"), off: !topLevel },
    { label: T.backward, icon: <KeyboardArrowDown fontSize="small" />, run: () => editor.order("backward"), off: !topLevel },
    { label: T.duplicate, icon: <ContentCopy fontSize="small" />, run: editor.duplicate, off: !topLevel || element.type === "group" },
    { label: T.delete, icon: <DeleteOutlined fontSize="small" />, run: editor.remove, off: false },
  ];
  return (
    <>
      {actions.map((action) => (
        <IconButton key={action.label} size="small" aria-label={action.label} title={action.label}
          disabled={action.off} onClick={action.run}>
          {action.icon}
        </IconButton>
      ))}
    </>
  );
}

/** The toolbar floats over the selected element. It flips below when there is no room above. */
export function ElementToolbar({ element, target, editor, hidden, onModal }: ElementToolbarProps): React.JSX.Element {
  const [dialog, setDialog] = useState<"cells" | "data" | "image" | null>(null);
  const [floating, setFloating] = useState<HTMLElement | null>(null);
  const { floatingStyles } = useFloating({
    placement: "top-start",
    middleware: [offset(GAP), flip(), shift({ padding: GAP })],
    whileElementsMounted: autoUpdate,
    elements: { reference: target, floating },
  });
  const open = (name: "cells" | "data" | "image"): void => {
    setDialog(name);
    onModal(true);
  };
  const close = (): void => {
    setDialog(null);
    onModal(false);
  };
  const save = (changes: Record<string, unknown>): void => {
    editor.patch(changes);
    close();
  };
  const typeName = EDITOR_TEXTS.types[element.type] ?? element.type;
  return (
    <>
      <Paper
        ref={setFloating}
        role="toolbar"
        aria-label={T.label(typeName)}
        elevation={0}
        style={{ ...floatingStyles, visibility: hidden ? "hidden" : "visible" }}
        sx={{ zIndex: 10, display: "flex", flexWrap: "wrap", alignItems: "center", gap: 0.5, p: 0.5,
          maxWidth: "min(100vw - 2rem, 56rem)", border: 1, borderColor: "divider", boxShadow: 3 }}
      >
        <TypeControls element={element} patch={editor.patch} editText={editor.startTextEdit} openDialog={open} />
        <Divider orientation="vertical" flexItem />
        <CommonControls element={element} editor={editor} />
      </Paper>
      <CellsDialog open={dialog === "cells"} element={element} onClose={close} onSave={save} />
      <DataDialog open={dialog === "data"} element={element} onClose={close} onSave={save} />
      <ImageUrlDialog open={dialog === "image"} initial={typeof element.props.src === "string" ? element.props.src : ""}
        onClose={close} onSave={(src) => save({ src })} />
    </>
  );
}
