import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import Card from "@mui/material/Card";
import CardActionArea from "@mui/material/CardActionArea";
import IconButton from "@mui/material/IconButton";
import Typography from "@mui/material/Typography";
import { Link } from "react-router-dom";

import { PhaseChip } from "@/features/projects/components/PhaseChip";
import { SlideThumbnail } from "@/features/projects/components/SlideThumbnail";
import { PROJECT_TEXTS } from "@/features/projects/texts";
import type { Project } from "@/features/projects/types";

interface ProjectCardProps {
  project: Project;
  onDelete: (project: Project) => void;
}

export function ProjectCard({ project, onDelete }: ProjectCardProps): React.JSX.Element {
  return (
    <Card component="li" className="relative flex flex-col">
      <CardActionArea component={Link} to={`/projects/${project.id}`}>
        <SlideThumbnail name={project.name} url={project.thumbnail_url} />
        <div className="flex flex-col gap-2 p-4">
          <Typography variant="h3" component="h2">
            {project.name}
          </Typography>
          <div className="flex justify-between gap-2">
            <PhaseChip phase={project.phase} />
            <Typography variant="caption" color="text.secondary">
              {project.slide_count > 0 ? PROJECT_TEXTS.slides(project.slide_count) : PROJECT_TEXTS.noSlides}
            </Typography>
          </div>
        </div>
      </CardActionArea>
      <IconButton
        aria-label={PROJECT_TEXTS.delete.action(project.name)}
        onClick={() => onDelete(project)}
        sx={{ position: "absolute", top: 1, right: 1, bgcolor: "background.paper", "&:hover": { bgcolor: "background.paper", color: "error.main" } }}
      >
        <DeleteOutlinedIcon fontSize="small" />
      </IconButton>
    </Card>
  );
}
