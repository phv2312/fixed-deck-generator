import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Markdown from "react-markdown";

import { ToolGroup } from "@/features/chat/components/ToolGroup";
import type { ChatMessage, ToolCall, ToolField } from "@/features/chat/types";
import type { LiveTurn } from "@/features/chat/turnReducer";

type ShowAll = (call: ToolCall, field: ToolField) => void;

export function UserMessage({ text }: { text: string }): React.JSX.Element {
  return (
    <Box
      sx={{ alignSelf: "flex-end", maxWidth: "85%", px: 2, py: 1.5, borderRadius: 1, bgcolor: "primary.main", color: "primary.contrastText", whiteSpace: "pre-wrap" }}
    >
      <Typography variant="body2">{text}</Typography>
    </Box>
  );
}

function AssistantText({ text }: { text: string }): React.JSX.Element {
  return (
    <Box sx={{ fontSize: "0.875rem", lineHeight: 1.5, "& p": { m: 0 }, "& p + p": { mt: 1 }, "& ul, & ol": { my: 1, pl: 3 }, wordBreak: "break-word" }}>
      <Markdown>{text}</Markdown>
    </Box>
  );
}

interface AssistantMessageProps {
  message: ChatMessage;
  onShowAll: ShowAll;
}

/** One assistant turn. A question turn shows the question as its text. */
export function AssistantMessage({ message, onShowAll }: AssistantMessageProps): React.JSX.Element {
  const text = message.text || message.question?.question || "";
  return (
    <div className="flex max-w-full flex-col gap-2">
      {message.tool_calls.length > 0 ? (
        <ToolGroup id={message.id} calls={message.tool_calls} onShowAll={onShowAll} />
      ) : null}
      {text ? <AssistantText text={text} /> : null}
    </div>
  );
}

interface LiveMessageProps {
  live: LiveTurn;
  onShowAll: ShowAll;
}

/** The turn that runs now: tools so far and the text that streams in. */
export function LiveMessage({ live, onShowAll }: LiveMessageProps): React.JSX.Element {
  return (
    <div className="flex max-w-full flex-col gap-2" aria-live="polite">
      {live.tools.length > 0 ? <ToolGroup id="live" calls={live.tools} live onShowAll={onShowAll} /> : null}
      {live.text ? <AssistantText text={live.text} /> : null}
      {live.status ? (
        <Typography variant="caption" color="text.secondary">
          {live.status}
        </Typography>
      ) : null}
    </div>
  );
}
