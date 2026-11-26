import Redo from "@mui/icons-material/Redo";
import Undo from "@mui/icons-material/Undo";
import WarningAmber from "@mui/icons-material/WarningAmber";
import Alert from "@mui/material/Alert";
import Button from "@mui/material/Button";
import Chip from "@mui/material/Chip";
import IconButton from "@mui/material/IconButton";
import Menu from "@mui/material/Menu";
import MenuItem from "@mui/material/MenuItem";
import Typography from "@mui/material/Typography";
import { useState } from "react";

import { ImageUrlDialog } from "@/features/deck-editor/components/toolbar/dialogs";
import { NEW_ELEMENT_DEFAULTS, PAGE_STEP } from "@/features/deck-editor/constants";
import type { DeckEditorState } from "@/features/deck-editor/hooks/useDeckEditor";
import { EDITOR_TEXTS } from "@/features/deck-editor/texts";
import type { NewKind } from "@/features/deck-editor/types";

const B = EDITOR_TEXTS.bar;
const KINDS = Object.keys(B.kinds) as NewKind[];

function AddMenu({ editor }: { editor: DeckEditorState }): React.JSX.Element {
  const [anchor, setAnchor] = useState<HTMLElement | null>(null);
  const [imageOpen, setImageOpen] = useState(false);
  const shift = ((editor.slide?.elements.length ?? 0) % 8) * PAGE_STEP;
  const place = (kind: NewKind): Record<string, number | string | object> => {
    const base: Record<string, number | string | object> = { ...NEW_ELEMENT_DEFAULTS[kind] };
    return { ...base, x: Number(base.x) + shift, y: Number(base.y) + shift };
  };
  const pick = (kind: NewKind): void => {
    setAnchor(null);
    if (kind === "image") setImageOpen(true);
    else editor.add(kind, place(kind));
  };
  return (
    <>
      <Button variant="outlined" aria-haspopup="menu" aria-expanded={anchor !== null} disabled={editor.locked}
        onClick={(event) => setAnchor(event.currentTarget)}>{B.add}</Button>
      <Menu anchorEl={anchor} open={anchor !== null} onClose={() => setAnchor(null)} aria-label={B.addMenu}>
        {KINDS.map((kind) => <MenuItem key={kind} onClick={() => pick(kind)}>{B.kinds[kind]}</MenuItem>)}
      </Menu>
      <ImageUrlDialog open={imageOpen} initial="" onClose={() => setImageOpen(false)}
        onSave={(src) => {
          setImageOpen(false);
          editor.add("image", { ...place("image"), src });
        }} />
    </>
  );
}

/** Add, undo, redo, the save state, the layout notes of the last edit, and a calm error notice. */
export function EditorBar({ editor }: { editor: DeckEditorState }): React.JSX.Element {
  const { deck, issues, notice, saving, locked } = editor;
  return (
    <div className="flex flex-col gap-2">
      <div className="flex flex-wrap items-center gap-2">
        <AddMenu editor={editor} />
        <IconButton aria-label={B.undo} title={B.undo} disabled={locked || !deck?.can_undo} onClick={editor.undo}><Undo /></IconButton>
        <IconButton aria-label={B.redo} title={B.redo} disabled={locked || !deck?.can_redo} onClick={editor.redo}><Redo /></IconButton>
        <Typography variant="caption" color="text.secondary" role="status" className="ml-auto">
          {saving ? B.saving : B.saved}
        </Typography>
        {issues.length > 0 && (
          <Chip icon={<WarningAmber />} color="warning" variant="outlined" label={EDITOR_TEXTS.issues.label(issues.length)}
            title={issues.map((issue) => issue.suggestion).join("\n")} />
        )}
      </div>
      {locked && <Alert severity="info" role="status">{EDITOR_TEXTS.locked}</Alert>}
      {notice && <Alert severity="info" onClose={editor.dismissNotice}>{notice}</Alert>}
    </div>
  );
}
