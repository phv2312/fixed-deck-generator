import Box from "@mui/material/Box";
import { useState } from "react";

import { Composer } from "@/features/chat/components/Composer";
import { FieldViewer } from "@/features/chat/components/FieldViewer";
import { MessageList } from "@/features/chat/components/MessageList";
import { CHAT_TEXTS } from "@/features/chat/texts";
import type { ToolCall, ToolField } from "@/features/chat/types";
import type { ChatTurn } from "@/features/chat/useChatTurn";

interface Viewing {
  title: string;
  field: ToolField;
}

interface ChatPanelProps {
  projectId: string;
  turn: ChatTurn;
}

/** The chat of one project: messages, the running turn, the composer, and the full-value viewer. */
export function ChatPanel({ projectId, turn }: ChatPanelProps): React.JSX.Element {
  const [viewing, setViewing] = useState<Viewing | null>(null);
  const showAll = (call: ToolCall, field: ToolField): void => setViewing({ title: `${call.name} · ${field.key}`, field });

  return (
    <Box
      component="section"
      aria-label={CHAT_TEXTS.panelLabel}
      sx={{ position: "relative", display: "flex", flexDirection: "column", height: "100%", minHeight: 0, bgcolor: "background.paper" }}
    >
      <MessageList projectId={projectId} turn={turn} onShowAll={showAll} />
      <Composer disabled={turn.busy} onSend={(message) => void turn.send(message)} />
      {viewing ? <FieldViewer title={viewing.title} field={viewing.field} onClose={() => setViewing(null)} /> : null}
    </Box>
  );
}
