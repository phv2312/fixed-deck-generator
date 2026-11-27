import Container from "@mui/material/Container";

import { ProjectsView } from "@/features/projects";

export function ProjectsPage(): React.JSX.Element {
  return (
    <Container component="main" maxWidth="xl" className="py-8">
      <ProjectsView />
    </Container>
  );
}
