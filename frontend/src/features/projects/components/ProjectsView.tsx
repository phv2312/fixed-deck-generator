import Button from "@mui/material/Button";
import Typography from "@mui/material/Typography";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { DeleteProjectDialog } from "@/features/projects/components/DeleteProjectDialog";
import { ProjectCard } from "@/features/projects/components/ProjectCard";
import { PAGE_SIZE } from "@/features/projects/constants";
import { useCreateProject, useProjects } from "@/features/projects/queries";
import { PROJECT_TEXTS } from "@/features/projects/texts";
import type { Project } from "@/features/projects/types";
import { errorText } from "@/shared/api";
import { EmptyState, ErrorState, LoadingState } from "@/shared/ui";

export function ProjectsView(): React.JSX.Element {
  const navigate = useNavigate();
  const projects = useProjects({ limit: PAGE_SIZE, offset: 0 });
  const create = useCreateProject();
  const onCreate = (): void => create.mutate({}, { onSuccess: (project) => void navigate(`/projects/${project.id}`) });
  const [deleting, setDeleting] = useState<Project | null>(null);

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <Typography variant="h1">{PROJECT_TEXTS.title}</Typography>
        <div className="flex items-center gap-4">
          {projects.data ? (
            <Typography color="text.secondary">{PROJECT_TEXTS.count(projects.data.total)}</Typography>
          ) : null}
          <Button variant="contained" disabled={create.isPending} onClick={onCreate}>
            {create.isPending ? PROJECT_TEXTS.creating : PROJECT_TEXTS.newDeck}
          </Button>
        </div>
      </div>
      {create.isError ? <Typography color="error" role="alert">{errorText(create.error)}</Typography> : null}
      <Content onCreate={onCreate} onDelete={setDeleting} query={projects} />
      <DeleteProjectDialog project={deleting} onClose={() => setDeleting(null)} />
    </div>
  );
}

interface ContentProps {
  query: ReturnType<typeof useProjects>;
  onCreate: () => void;
  onDelete: (project: Project) => void;
}

function Content({ query, onCreate, onDelete }: ContentProps): React.JSX.Element {
  if (query.isPending) return <LoadingState />;
  if (query.isError) return <ErrorState error={query.error} onRetry={() => void query.refetch()} />;
  if (query.data.items.length === 0) {
    return (
      <EmptyState
        title={PROJECT_TEXTS.empty.title}
        hint={PROJECT_TEXTS.empty.hint}
        actionLabel={PROJECT_TEXTS.newDeck}
        onAction={onCreate}
      />
    );
  }
  return (
    <ul className="m-0 grid list-none grid-cols-[repeat(auto-fill,minmax(18rem,1fr))] gap-6 p-0">
      {query.data.items.map((project) => (
        <ProjectCard key={project.id} project={project} onDelete={onDelete} />
      ))}
    </ul>
  );
}
