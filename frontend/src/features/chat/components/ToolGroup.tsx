import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import Box from "@mui/material/Box";
import ButtonBase from "@mui/material/ButtonBase";
import Typography from "@mui/material/Typography";
import { useState } from "react";

import { ToolRow } from "@/features/chat/components/ToolRow";
import { countTools } from "@/features/chat/format";
import { CHAT_TEXTS } from "@/features/chat/texts";
import type { ToolCall, ToolField } from "@/features/chat/types";

interface ToolGroupProps {
  id: string;
  calls: ToolCall[];
  /** The group of a running turn shows its title as "Using tools". */
  live?: boolean;
  onShowAll: (call: ToolCall, field: ToolField) => void;
}

/** All tool calls of one assistant turn behind one expander. */
export function ToolGroup({ id, calls, live = false, onShowAll }: ToolGroupProps): React.JSX.Element {
  const counts = countTools(calls);
  const [open, setOpen] = useState(false);
  const listId = `tools-${id}`;
  const title = live ? CHAT_TEXTS.tools.using : CHAT_TEXTS.tools.used(calls.length);
  return (
    <div className="flex flex-col gap-1">
      <ButtonBase
        onClick={() => setOpen(!open)}
        aria-expanded={open}
        aria-controls={listId}
        sx={{ display: "flex", gap: 1, px: 1.5, minHeight: 44, border: 1, borderColor: "divider", borderRadius: 1, bgcolor: "background.default", textAlign: "left", justifyContent: "flex-start" }}
      >
        <ExpandMoreIcon aria-hidden fontSize="small" sx={{ transform: open ? "none" : "rotate(-90deg)" }} />
        <Typography variant="body2" sx={{ fontWeight: 600 }}>
          {title}
        </Typography>
        <Typography variant="caption" color={counts.failed > 0 ? "error.main" : "text.secondary"} sx={{ ml: "auto" }}>
          {CHAT_TEXTS.tools.summary(counts)}
        </Typography>
      </ButtonBase>
      {open ? (
        <Box
          component="ul"
          id={listId}
          sx={{ m: 0, p: 0, listStyle: "none", maxHeight: 360, overflowY: "auto", border: 1, borderColor: "divider", borderRadius: 1 }}
        >
          {calls.map((call) => (
            <ToolRow key={call.id} call={call} onShowAll={onShowAll} />
          ))}
        </Box>
      ) : null}
    </div>
  );
}
