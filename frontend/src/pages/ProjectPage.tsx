import AppBar from "@mui/material/AppBar";
import Box from "@mui/material/Box";
import Link from "@mui/material/Link";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";
import { useQueryClient } from "@tanstack/react-query";
import { Link as RouterLink, useParams } from "react-router-dom";

import { ChatPanel, useChatTurn, type StreamEvent } from "@/features/chat";
import { refreshPlan } from "@/features/interview";
import { PhaseChip, invalidateProjects, useProject } from "@/features/projects";
import { ProjectPane } from "@/pages/project/ProjectPane";
import { PAGE_TEXTS } from "@/pages/texts";
import { ErrorState, LoadingState } from "@/shared/ui";

const REFRESH_EVENTS: ReadonlySet<StreamEvent["type"]> = new Set(["question", "plan_updated", "deck_ready", "done"]);

export function ProjectPage(): React.JSX.Element {
  const { projectId = "" } = useParams();
  const client = useQueryClient();
  const project = useProject(projectId);
  const turn = useChatTurn({
    projectId,
    onEvent: (event) => {
      if (!REFRESH_EVENTS.has(event.type)) return;
      void refreshPlan(client, projectId);
      void invalidateProjects(client);
    },
  });

  return (
    <div className="flex min-h-dvh flex-col lg:h-dvh">
      <AppBar position="static" color="inherit" elevation={0} sx={{ borderBottom: 1, borderColor: "divider" }}>
        <Toolbar className="flex flex-wrap gap-4">
          <Link component={RouterLink} to="/" sx={{ minHeight: 44, display: "inline-flex", alignItems: "center" }}>
            {PAGE_TEXTS.backToDecks}
          </Link>
          <Typography variant="h3" component="h1">
            {project.data?.name ?? projectId}
          </Typography>
          {project.data ? <PhaseChip phase={project.data.phase} /> : null}
        </Toolbar>
      </AppBar>
      <div className="grid min-h-0 flex-1 grid-cols-1 lg:grid-cols-[24rem_1fr] lg:grid-rows-[minmax(0,1fr)]">
        <Box component="aside" sx={{ order: { xs: 2, lg: 1 }, borderRight: { lg: 1 }, borderTop: { xs: 1, lg: 0 }, borderColor: "divider", height: { xs: "32rem", lg: "auto" }, minHeight: 0, overflow: "hidden" }}>
          <ChatPanel projectId={projectId} turn={turn} />
        </Box>
        <main aria-label={PAGE_TEXTS.rightPane} className="order-1 min-h-0 overflow-y-auto p-6 lg:order-2 lg:p-8">
          {project.isPending ? <LoadingState /> : null}
          {project.isError ? <ErrorState error={project.error} onRetry={() => void project.refetch()} /> : null}
          {project.data ? <ProjectPane project={project.data} turn={turn} /> : null}
        </main>
      </div>
    </div>
  );
}
