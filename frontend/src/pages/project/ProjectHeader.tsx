import ArrowBack from "@mui/icons-material/ArrowBack";
import ChevronLeft from "@mui/icons-material/ChevronLeft";
import IconButton from "@mui/material/IconButton";
import Typography from "@mui/material/Typography";
import { Link as RouterLink } from "react-router-dom";

import { PhaseChip, projectTitle, type Project } from "@/features/projects";
import { PAGE_TEXTS } from "@/pages/texts";

interface ProjectHeaderProps {
  project: Project | undefined;
  /** True when the project cannot be opened. The header then shows a plain notice instead of a name. */
  failed: boolean;
  /** True while the assistant works. */
  working: boolean;
  /** Folds the chat into the side rail. Without it the header shows no fold button. */
  onCollapse?: () => void;
}

/** The way back, the name and the state of the project. It sits at the top of the chat column. */
export function ProjectHeader({ project, failed, working, onCollapse }: ProjectHeaderProps): React.JSX.Element {
  const name = project ? projectTitle(project) : failed ? PAGE_TEXTS.unknownProject : "";
  return (
    <div className="flex min-w-0 items-center gap-2 px-2 py-1">
      <IconButton component={RouterLink} to="/" size="small" aria-label={PAGE_TEXTS.backToDecks} title={PAGE_TEXTS.backToDecks}>
        <ArrowBack />
      </IconButton>
      <Typography variant="h3" component="h1" noWrap title={name} sx={{ minWidth: 0, flex: "0 1 auto" }}>{name}</Typography>
      {project ? <PhaseChip phase={project.phase} working={working} /> : null}
      {onCollapse ? (
        <IconButton size="small" aria-label={PAGE_TEXTS.collapseChat} title={PAGE_TEXTS.collapseChat} onClick={onCollapse} sx={{ ml: "auto" }}>
          <ChevronLeft />
        </IconButton>
      ) : null}
    </div>
  );
}
