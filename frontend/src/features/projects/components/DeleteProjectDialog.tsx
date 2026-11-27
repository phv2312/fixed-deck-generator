import Button from "@mui/material/Button";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";

import { useDeleteProject } from "@/features/projects/queries";
import { projectTitle } from "@/features/projects/title";
import { PROJECT_TEXTS } from "@/features/projects/texts";
import type { Project } from "@/features/projects/types";
import { errorText } from "@/shared/api";
import { SHARED_TEXTS } from "@/shared/texts";

interface DeleteProjectDialogProps {
  project: Project | null;
  onClose: () => void;
}

export function DeleteProjectDialog({ project, onClose }: DeleteProjectDialogProps): React.JSX.Element {
  const remove = useDeleteProject();

  const confirm = (): void => {
    if (project) remove.mutate(project.id, { onSuccess: onClose });
  };

  return (
    <Dialog open={project !== null} onClose={onClose} fullWidth maxWidth="xs">
      <DialogTitle>{PROJECT_TEXTS.delete.title}</DialogTitle>
      <DialogContent>
        <DialogContentText>{project ? PROJECT_TEXTS.delete.body(projectTitle(project)) : null}</DialogContentText>
        {remove.isError ? (
          <DialogContentText color="error" role="alert">
            {errorText(remove.error)}
          </DialogContentText>
        ) : null}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>{SHARED_TEXTS.cancel}</Button>
        <Button color="error" variant="contained" onClick={confirm} disabled={remove.isPending}>
          {remove.isPending ? PROJECT_TEXTS.delete.submitting : PROJECT_TEXTS.delete.confirm}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
