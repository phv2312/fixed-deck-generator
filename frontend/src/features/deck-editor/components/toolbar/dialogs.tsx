import AddOutlined from "@mui/icons-material/AddOutlined";
import DeleteOutlined from "@mui/icons-material/DeleteOutlined";
import Button from "@mui/material/Button";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";
import IconButton from "@mui/material/IconButton";
import TextField from "@mui/material/TextField";
import { Fragment, useState } from "react";

import {
  canRemoveColumn, canRemoveRow, columnCount, insertColumnRight, insertRowBelow, removeColumn, removeRow, setCell, toChanges, toDraft,
} from "@/features/deck-editor/table";
import { EDITOR_TEXTS } from "@/features/deck-editor/texts";
import type { DeckElement } from "@/features/deck-editor/types";

const D = EDITOR_TEXTS.dialog;

interface DialogProps {
  element: DeckElement;
  open: boolean;
  onClose: () => void;
  onSave: (changes: Record<string, unknown>) => void;
}

function Actions({ onClose, onSave, disabled }: { onClose: () => void; onSave: () => void; disabled?: boolean }): React.JSX.Element {
  return (
    <DialogActions>
      <Button onClick={onClose}>{D.cancel}</Button>
      <Button variant="contained" onClick={onSave} disabled={disabled}>{D.save}</Button>
    </DialogActions>
  );
}

function CellsForm({ element, onClose, onSave }: Omit<DialogProps, "open">): React.JSX.Element {
  const [draft, setDraft] = useState(() => toDraft(element.props));
  const columns = columnCount(draft);
  const grid = { gridTemplateColumns: `repeat(${columns.toString()}, minmax(0, 1fr)) auto` };
  return (
    <>
      <DialogContent>
        <div className="grid items-center gap-2 pt-2" style={grid}>
          {Array.from({ length: columns }, (_, c) => (
            <div key={`col-${c.toString()}`} className="flex justify-end">
              <IconButton size="small" aria-label={D.insertColumnAfter(c + 1)} onClick={() => setDraft(insertColumnRight(draft, c))}>
                <AddOutlined fontSize="small" />
              </IconButton>
              <IconButton size="small" aria-label={D.removeColumnAt(c + 1)} disabled={!canRemoveColumn(draft)} onClick={() => setDraft(removeColumn(draft, c))}>
                <DeleteOutlined fontSize="small" />
              </IconButton>
            </div>
          ))}
          <span />
          {draft.rows.map((row, r) => (
            <Fragment key={`row-${r.toString()}`}>
              {row.map((cell, c) => (
                <TextField
                  key={`cell-${r.toString()}-${c.toString()}`}
                  size="small"
                  value={cell}
                  onChange={(event) => setDraft(setCell(draft, r, c, event.target.value))}
                  slotProps={{ htmlInput: { "aria-label": D.cell(r + 1, c + 1) } }}
                />
              ))}
              <div className="flex">
                <IconButton size="small" aria-label={D.insertRowBelow(r + 1)} onClick={() => setDraft(insertRowBelow(draft, r))}>
                  <AddOutlined fontSize="small" />
                </IconButton>
                <IconButton size="small" aria-label={D.removeRowAt(r + 1)} disabled={!canRemoveRow(draft, r)} onClick={() => setDraft(removeRow(draft, r))}>
                  <DeleteOutlined fontSize="small" />
                </IconButton>
              </div>
            </Fragment>
          ))}
        </div>
        <TextField
          label={D.caption}
          size="small"
          fullWidth
          value={draft.caption}
          onChange={(event) => setDraft({ ...draft, caption: event.target.value })}
          sx={{ mt: 2 }}
        />
      </DialogContent>
      <Actions onClose={onClose} onSave={() => onSave(toChanges(draft))} />
    </>
  );
}

/** Edit the cells of a table. The dialog stays mounted only while open, so its draft is fresh. */
export function CellsDialog(props: DialogProps): React.JSX.Element {
  return (
    <Dialog open={props.open} onClose={props.onClose} maxWidth="md" fullWidth>
      <DialogTitle>{D.cellsTitle}</DialogTitle>
      {props.open && <CellsForm element={props.element} onClose={props.onClose} onSave={props.onSave} />}
    </Dialog>
  );
}

function parseData(text: string): Record<string, unknown> | null {
  try {
    const value: unknown = JSON.parse(text);
    return typeof value === "object" && value !== null && !Array.isArray(value) ? (value as Record<string, unknown>) : null;
  } catch {
    return null;
  }
}

function DataForm({ element, onClose, onSave }: Omit<DialogProps, "open">): React.JSX.Element {
  const [text, setText] = useState(() => JSON.stringify(element.props.data ?? {}, null, 2));
  const parsed = parseData(text);
  return (
    <>
      <DialogContent>
        <TextField
          label={D.dataField}
          multiline
          minRows={8}
          fullWidth
          value={text}
          onChange={(event) => setText(event.target.value)}
          error={parsed === null}
          helperText={parsed === null ? D.dataInvalid : " "}
          sx={{ mt: 1 }}
        />
      </DialogContent>
      <Actions onClose={onClose} onSave={() => parsed && onSave({ data: parsed })} disabled={parsed === null} />
    </>
  );
}

export function DataDialog(props: DialogProps): React.JSX.Element {
  return (
    <Dialog open={props.open} onClose={props.onClose} maxWidth="sm" fullWidth>
      <DialogTitle>{D.dataTitle}</DialogTitle>
      {props.open && <DataForm element={props.element} onClose={props.onClose} onSave={props.onSave} />}
    </Dialog>
  );
}

interface ImageUrlDialogProps {
  open: boolean;
  initial: string;
  onClose: () => void;
  onSave: (src: string) => void;
}

function ImageUrlForm({ initial, onClose, onSave }: Omit<ImageUrlDialogProps, "open">): React.JSX.Element {
  const [src, setSrc] = useState(initial);
  const valid = /^https?:\/\//.test(src);
  return (
    <>
      <DialogContent>
        <TextField label={D.imageField} helperText={D.imageHint} fullWidth value={src}
          onChange={(event) => setSrc(event.target.value)} sx={{ mt: 1 }} />
      </DialogContent>
      <Actions onClose={onClose} onSave={() => onSave(src)} disabled={!valid} />
    </>
  );
}

/** Ask for an image address. Used to change an image and to add a new one. */
export function ImageUrlDialog(props: ImageUrlDialogProps): React.JSX.Element {
  return (
    <Dialog open={props.open} onClose={props.onClose} maxWidth="sm" fullWidth>
      <DialogTitle>{D.imageTitle}</DialogTitle>
      {props.open && <ImageUrlForm initial={props.initial} onClose={props.onClose} onSave={props.onSave} />}
    </Dialog>
  );
}
