import Box from "@mui/material/Box";
import { useState } from "react";
import { useParams } from "react-router-dom";

import { isProjectNotFound, useProject } from "@/features/projects";
import { ChatSidebar } from "@/pages/project/ChatSidebar";
import { ProjectHeader } from "@/pages/project/ProjectHeader";
import { ProjectPane } from "@/pages/project/ProjectPane";
import { useProjectTurn } from "@/pages/project/useProjectTurn";
import { PAGE_TEXTS } from "@/pages/texts";
import { ErrorState, LoadingState } from "@/shared/ui";

export function ProjectPage(): React.JSX.Element {
  const { projectId = "" } = useParams();
  const project = useProject(projectId);
  const turn = useProjectTurn(projectId);
  const [chatOpen, setChatOpen] = useState(true);
  const retry = isProjectNotFound(project.error) ? undefined : () => void project.refetch();

  return (
    <div className="flex min-h-dvh flex-col lg:h-dvh">
      <Box sx={{ display: { lg: "none" }, borderBottom: 1, borderColor: "divider" }}>
        <ProjectHeader project={project.data} failed={project.isError} working={turn.busy} />
      </Box>
      {/* The workspace comes first in the document, so Tab follows the screen order on a narrow screen. */}
      <div className={`grid min-h-0 flex-1 grid-cols-1 ${chatOpen ? "lg:grid-cols-[24rem_1fr]" : "lg:grid-cols-[3.5rem_1fr]"} lg:grid-rows-[minmax(0,1fr)]`}>
        <main aria-label={PAGE_TEXTS.rightPane} className="min-h-0 overflow-y-auto p-6 lg:col-start-2 lg:row-start-1 lg:p-8">
          {project.isPending ? <LoadingState /> : null}
          {project.isError ? <ErrorState error={project.error} onRetry={retry} /> : null}
          {project.data ? <ProjectPane project={project.data} turn={turn} onAskAi={() => setChatOpen(true)} /> : null}
        </main>
        <ChatSidebar projectId={projectId} project={project.data} turn={turn} unavailable={project.isError} open={chatOpen} onOpenChange={setChatOpen} />
      </div>
    </div>
  );
}
