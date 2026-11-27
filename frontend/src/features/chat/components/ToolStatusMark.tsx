import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";

import { CHAT_TEXTS } from "@/features/chat/texts";
import type { ToolStatus } from "@/features/chat/types";

const STYLES: Record<ToolStatus, { color: string; clipPath: string }> = {
  running: { color: "info.main", clipPath: "polygon(50% 0, 100% 100%, 0 100%)" },
  done: { color: "success.main", clipPath: "circle(50%)" },
  error: { color: "error.main", clipPath: "inset(0)" },
};

/** The status of a tool call. Each status has its own shape and its own word. */
export function ToolStatusMark({ status }: { status: ToolStatus }): React.JSX.Element {
  const style = STYLES[status];
  return (
    <span className="flex shrink-0 items-center gap-1">
      <Box aria-hidden sx={{ width: 8, height: 8, bgcolor: style.color, clipPath: style.clipPath }} />
      <Typography variant="caption" sx={{ color: style.color, fontWeight: 600 }}>
        {CHAT_TEXTS.tools.status[status]}
      </Typography>
    </span>
  );
}
