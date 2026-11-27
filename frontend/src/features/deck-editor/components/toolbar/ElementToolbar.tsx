import ContentCopy from "@mui/icons-material/ContentCopy";
import DeleteOutlined from "@mui/icons-material/DeleteOutlined";
import KeyboardArrowDown from "@mui/icons-material/KeyboardArrowDown";
import KeyboardArrowUp from "@mui/icons-material/KeyboardArrowUp";
import MoreHoriz from "@mui/icons-material/MoreHoriz";
import ListItemIcon from "@mui/material/ListItemIcon";
import Menu from "@mui/material/Menu";
import MenuItem from "@mui/material/MenuItem";
import IconButton from "@mui/material/IconButton";
import Paper from "@mui/material/Paper";
import { alpha } from "@mui/material/styles";
import { autoUpdate, flip, offset, shift, size, useFloating } from "@floating-ui/react";
import { useLayoutEffect, useState } from "react";

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
  /** True on a narrow screen: the toolbar sits under the slide and does not cover it. */
  docked: boolean;
  onModal: (open: boolean) => void;
}

/** The less used actions sit in one overflow menu, so the bar stays short. */
function MoreMenu({ element, editor }: { element: DeckElement; editor: DeckEditorState }): React.JSX.Element {
  const [anchor, setAnchor] = useState<HTMLElement | null>(null);
  const topLevel = element.parent_id === null;
  const actions = [
    { label: T.forward, icon: <KeyboardArrowUp fontSize="small" />, run: () => editor.order("forward"), off: !topLevel },
    { label: T.backward, icon: <KeyboardArrowDown fontSize="small" />, run: () => editor.order("backward"), off: !topLevel },
    { label: T.duplicate, icon: <ContentCopy fontSize="small" />, run: editor.duplicate, off: !topLevel || element.type === "group" },
    { label: T.delete, icon: <DeleteOutlined fontSize="small" />, run: editor.remove, off: false },
  ];
  return (
    <>
      <IconButton size="small" aria-label={T.more} title={T.more} aria-haspopup="menu" aria-expanded={anchor !== null}
        onClick={(event) => setAnchor(event.currentTarget)}>
        <MoreHoriz fontSize="small" />
      </IconButton>
      <Menu anchorEl={anchor} open={anchor !== null} onClose={() => setAnchor(null)}>
        {actions.map((action) => (
          <MenuItem key={action.label} disabled={action.off} onClick={() => { setAnchor(null); action.run(); }}>
            <ListItemIcon>{action.icon}</ListItemIcon>
            {action.label}
          </MenuItem>
        ))}
      </Menu>
    </>
  );
}

/** The toolbar floats over the selected element, or sits under the slide on a narrow screen. */
export function ElementToolbar({ element, target, editor, hidden, docked, onModal }: ElementToolbarProps): React.JSX.Element {
  const [dialog, setDialog] = useState<"cells" | "data" | "image" | null>(null);
  /** The slide stage. The toolbar stays inside it, so it does not cover the slide list. */
  const stage = target.parentElement ?? undefined;
  const { floatingStyles, refs } = useFloating({
    placement: "top-start",
    middleware: [
      offset(GAP),
      flip({ boundary: stage }),
      size({
        boundary: stage,
        apply: ({ availableWidth, elements }) => {
          elements.floating.style.maxWidth = `${availableWidth}px`;
        },
      }),
      shift({ boundary: stage, padding: GAP }),
    ],
    whileElementsMounted: autoUpdate,
  });
  const { setReference, setFloating } = refs;
  /** The reference follows the selected element. A new selection moves the toolbar at once. */
  useLayoutEffect(() => setReference(docked ? null : target), [setReference, docked, target]);
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
        style={{ ...(docked ? {} : floatingStyles), visibility: hidden ? "hidden" : "visible" }}
        sx={(theme) => ({
          /* Above every element box, whatever its stacking order. */
          zIndex: docked ? "auto" : theme.zIndex.speedDial, display: "flex", flexWrap: "wrap", alignItems: "center", gap: 0.25, px: 0.5, py: 0.25,
          width: "fit-content", borderRadius: 1, boxShadow: 4, bgcolor: "text.primary", color: "background.paper",
          "& .MuiIconButton-root, & .MuiToggleButton-root, & .MuiInputBase-root, & .MuiNativeSelect-icon": { color: "inherit" },
          "& .MuiToggleButton-root.Mui-selected": { color: "inherit", bgcolor: alpha(theme.palette.common.white, 0.18) },
          "& .MuiToggleButton-root:hover, & .MuiIconButton-root:hover": { bgcolor: alpha(theme.palette.common.white, 0.12) },
          "& .MuiNativeSelect-select option": { color: "text.primary" },
          "& fieldset": { border: 0 },
        })}
      >
        <TypeControls element={element} patch={editor.patch} editText={editor.startTextEdit} openDialog={open} />
        <MoreMenu element={element} editor={editor} />
      </Paper>
      <CellsDialog open={dialog === "cells"} element={element} onClose={close} onSave={save} />
      <DataDialog open={dialog === "data"} element={element} onClose={close} onSave={save} />
      <ImageUrlDialog open={dialog === "image"} initial={typeof element.props.src === "string" ? element.props.src : ""}
        onClose={close} onSave={(src) => save({ src })} />
    </>
  );
}
