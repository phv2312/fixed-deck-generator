import ArrowBack from "@mui/icons-material/ArrowBack";
import ChatBubbleOutlined from "@mui/icons-material/ChatBubbleOutlined";
import Box from "@mui/material/Box";
import IconButton from "@mui/material/IconButton";
import { Link as RouterLink } from "react-router-dom";

import { ChatPanel, type ChatTurn } from "@/features/chat";
import type { Project } from "@/features/projects";
import { ProjectHeader } from "@/pages/project/ProjectHeader";
import { PAGE_TEXTS } from "@/pages/texts";

interface ChatSidebarProps {
  projectId: string;
  project: Project | undefined;
  turn: ChatTurn;
  unavailable: boolean;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

/** The project header and the chat as a side column. On a wide screen it folds into a narrow rail. */
export function ChatSidebar({ projectId, project, turn, unavailable, open, onOpenChange }: ChatSidebarProps): React.JSX.Element {
  return (
    <Box
      component="aside"
      className="lg:col-start-1 lg:row-start-1"
      sx={{ borderStyle: "solid", borderColor: "divider", borderWidth: 0, borderTopWidth: { xs: 1, lg: 0 }, borderRightWidth: { lg: 1 }, height: { xs: "32rem", lg: "auto" }, minHeight: 0, overflow: "hidden" }}
    >
      <Box sx={{ display: open ? "flex" : { xs: "flex", lg: "none" }, flexDirection: "column", height: "100%" }}>
        <Box sx={{ display: { xs: "none", lg: "block" }, borderBottom: 1, borderColor: "divider" }}>
          <ProjectHeader project={project} failed={unavailable} working={turn.busy} onCollapse={() => onOpenChange(false)} />
        </Box>
        <Box sx={{ flex: 1, minHeight: 0 }}>
          <ChatPanel projectId={projectId} turn={turn} unavailable={unavailable} />
        </Box>
      </Box>
      {open ? null : (
        <Box sx={{ display: { xs: "none", lg: "flex" }, flexDirection: "column", alignItems: "center", gap: 0.5, py: 1 }}>
          <IconButton component={RouterLink} to="/" aria-label={PAGE_TEXTS.backToDecks} title={PAGE_TEXTS.backToDecks}>
            <ArrowBack />
          </IconButton>
          <IconButton aria-label={PAGE_TEXTS.openChat} title={PAGE_TEXTS.openChat} onClick={() => onOpenChange(true)}>
            <ChatBubbleOutlined />
          </IconButton>
        </Box>
      )}
    </Box>
  );
}
