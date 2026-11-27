import AutoAwesome from "@mui/icons-material/AutoAwesome";
import BarChartOutlined from "@mui/icons-material/BarChartOutlined";
import CategoryOutlined from "@mui/icons-material/CategoryOutlined";
import ImageOutlined from "@mui/icons-material/ImageOutlined";
import Redo from "@mui/icons-material/Redo";
import TableChartOutlined from "@mui/icons-material/TableChartOutlined";
import TextFields from "@mui/icons-material/TextFields";
import Undo from "@mui/icons-material/Undo";
import WarningAmber from "@mui/icons-material/WarningAmber";
import Alert from "@mui/material/Alert";
import Button from "@mui/material/Button";
import Chip from "@mui/material/Chip";
import Divider from "@mui/material/Divider";
import IconButton from "@mui/material/IconButton";
import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import { useState } from "react";

import { ImageUrlDialog } from "@/features/deck-editor/components/toolbar/dialogs";
import { NEW_ELEMENT_DEFAULTS, PAGE_STEP } from "@/features/deck-editor/constants";
import type { DeckEditorState } from "@/features/deck-editor/hooks/useDeckEditor";
import { EDITOR_TEXTS } from "@/features/deck-editor/texts";
import type { NewKind } from "@/features/deck-editor/types";

const B = EDITOR_TEXTS.bar;
const ICONS: Record<NewKind, React.JSX.Element> = {
  text: <TextFields />, image: <ImageOutlined />, table: <TableChartOutlined />,
  shape: <CategoryOutlined />, chart: <BarChartOutlined />,
};
const KINDS = Object.keys(ICONS) as NewKind[];

/** One icon per element kind. A click adds that element to the slide. */
function AddButtons({ editor }: { editor: DeckEditorState }): React.JSX.Element {
  const [imageOpen, setImageOpen] = useState(false);
  const shift = ((editor.slide?.elements.length ?? 0) % 8) * PAGE_STEP;
  const place = (kind: NewKind): Record<string, number | string | object> => {
    const base: Record<string, number | string | object> = { ...NEW_ELEMENT_DEFAULTS[kind] };
    return { ...base, x: Number(base.x) + shift, y: Number(base.y) + shift };
  };
  const pick = (kind: NewKind): void => {
    if (kind === "image") setImageOpen(true);
    else editor.add(kind, place(kind));
  };
  return (
    <>
      {KINDS.map((kind) => (
        <IconButton key={kind} aria-label={B.kinds[kind]} title={B.kinds[kind]} disabled={editor.locked} onClick={() => pick(kind)}>
          {ICONS[kind]}
        </IconButton>
      ))}
      <ImageUrlDialog open={imageOpen} initial="" onClose={() => setImageOpen(false)}
        onSave={(src) => {
          setImageOpen(false);
          editor.add("image", { ...place("image"), src });
        }} />
    </>
  );
}

interface EditorBarProps {
  editor: DeckEditorState;
  /** Opens the chat sidebar, so the user can ask the assistant. */
  onAskAi: () => void;
}

/** One short bar: add an element, undo, redo, ask the assistant. The save state and notes sit beside it. */
export function EditorBar({ editor, onAskAi }: EditorBarProps): React.JSX.Element {
  const { deck, issues, notice, saving, locked } = editor;
  return (
    <div className="flex flex-col gap-2">
      <div className="flex flex-wrap items-center justify-center gap-3">
        <Paper elevation={0} sx={{ display: "flex", alignItems: "center", gap: 0.5, p: 0.5, borderRadius: 1, border: 1, borderColor: "divider", boxShadow: 2 }}>
          <AddButtons editor={editor} />
          <Divider orientation="vertical" flexItem />
          <IconButton aria-label={B.undo} title={B.undo} disabled={locked || !deck?.can_undo} onClick={editor.undo}><Undo /></IconButton>
          <IconButton aria-label={B.redo} title={B.redo} disabled={locked || !deck?.can_redo} onClick={editor.redo}><Redo /></IconButton>
          <Divider orientation="vertical" flexItem />
          <Button startIcon={<AutoAwesome />} onClick={onAskAi} sx={{ borderRadius: 0.5 }}>{B.askAi}</Button>
        </Paper>
        <Typography variant="caption" color="text.secondary" role="status">
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
