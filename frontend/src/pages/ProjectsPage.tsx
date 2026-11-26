import AppBar from "@mui/material/AppBar";
import Container from "@mui/material/Container";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";

import { ProjectsView } from "@/features/projects";
import { SHARED_TEXTS } from "@/shared/texts";

export function ProjectsPage(): React.JSX.Element {
  return (
    <>
      <AppBar position="static" color="inherit" elevation={0} sx={{ borderBottom: 1, borderColor: "divider" }}>
        <Toolbar>
          <Typography variant="h3" component="p">
            {SHARED_TEXTS.appName}
          </Typography>
        </Toolbar>
      </AppBar>
      <Container component="main" maxWidth="xl" className="py-8">
        <ProjectsView />
      </Container>
    </>
  );
}
