import Button from "@mui/material/Button";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";
import TextField from "@mui/material/TextField";
import { useState, type FormEvent } from "react";

import { useCreateProject } from "@/features/projects/queries";
import { PROJECT_TEXTS } from "@/features/projects/texts";
import type { Project } from "@/features/projects/types";
import { errorText } from "@/shared/api";
import { SHARED_TEXTS } from "@/shared/texts";

interface NewProjectDialogProps {
  open: boolean;
  onClose: () => void;
  onCreated: (project: Project) => void;
}

export function NewProjectDialog({ open, onClose, onCreated }: NewProjectDialogProps): React.JSX.Element {
  const [name, setName] = useState("");
  const create = useCreateProject();

  const submit = (event: FormEvent): void => {
    event.preventDefault();
    create.mutate({ name: name.trim() }, { onSuccess: onCreated });
  };

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="xs" component="form" onSubmit={submit}>
      <DialogTitle>{PROJECT_TEXTS.create.title}</DialogTitle>
      <DialogContent>
        <TextField
          required
          fullWidth
          margin="dense"
          label={PROJECT_TEXTS.create.nameLabel}
          value={name}
          onChange={(event) => setName(event.target.value)}
          error={create.isError}
          helperText={create.isError ? errorText(create.error) : undefined}
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>{SHARED_TEXTS.cancel}</Button>
        <Button type="submit" variant="contained" disabled={create.isPending || name.trim() === ""}>
          {create.isPending ? PROJECT_TEXTS.create.submitting : PROJECT_TEXTS.create.submit}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
