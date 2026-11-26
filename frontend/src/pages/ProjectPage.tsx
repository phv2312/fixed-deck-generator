import AppBar from "@mui/material/AppBar";
import Box from "@mui/material/Box";
import Link from "@mui/material/Link";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";
import { Link as RouterLink, useParams } from "react-router-dom";

import { ChatPanel } from "@/features/chat";
import { PhaseChip, isProjectNotFound, useProject } from "@/features/projects";
import { ProjectPane } from "@/pages/project/ProjectPane";
import { useProjectTurn } from "@/pages/project/useProjectTurn";
import { PAGE_TEXTS } from "@/pages/texts";
import { ErrorState, LoadingState } from "@/shared/ui";

export function ProjectPage(): React.JSX.Element {
  const { projectId = "" } = useParams();
  const project = useProject(projectId);
  const turn = useProjectTurn(projectId);
  const retry = isProjectNotFound(project.error) ? undefined : () => void project.refetch();

  return (
    <div className="flex min-h-dvh flex-col lg:h-dvh">
      <AppBar position="static" color="inherit" elevation={0} sx={{ borderBottom: 1, borderColor: "divider" }}>
        <Toolbar className="flex flex-wrap gap-4">
          <Link component={RouterLink} to="/" sx={{ minHeight: 44, display: "inline-flex", alignItems: "center" }}>
            {PAGE_TEXTS.backToDecks}
          </Link>
          <Typography variant="h3" component="h1">
            {project.data?.name ?? (project.isError ? PAGE_TEXTS.unknownProject : "")}
          </Typography>
          {project.data ? <PhaseChip phase={project.data.phase} /> : null}
        </Toolbar>
      </AppBar>
      {/* The workspace comes first in the document, so Tab follows the screen order on a narrow screen. */}
      <div className="grid min-h-0 flex-1 grid-cols-1 lg:grid-cols-[24rem_1fr] lg:grid-rows-[minmax(0,1fr)]">
        <main aria-label={PAGE_TEXTS.rightPane} className="min-h-0 overflow-y-auto p-6 lg:col-start-2 lg:row-start-1 lg:p-8">
          {project.isPending ? <LoadingState /> : null}
          {project.isError ? <ErrorState error={project.error} onRetry={retry} /> : null}
          {project.data ? <ProjectPane project={project.data} turn={turn} /> : null}
        </main>
        <Box
          component="aside"
          className="lg:col-start-1 lg:row-start-1"
          sx={{ borderStyle: "solid", borderColor: "divider", borderWidth: 0, borderTopWidth: { xs: 1, lg: 0 }, borderRightWidth: { lg: 1 }, height: { xs: "32rem", lg: "auto" }, minHeight: 0, overflow: "hidden" }}
        >
          <ChatPanel projectId={projectId} turn={turn} unavailable={project.isError} />
        </Box>
      </div>
    </div>
  );
}
