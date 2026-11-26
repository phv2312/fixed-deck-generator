import Box from "@mui/material/Box";
import ButtonBase from "@mui/material/ButtonBase";
import Typography from "@mui/material/Typography";
import { useState } from "react";

import { ToolFieldView } from "@/features/chat/components/ToolFieldView";
import { ToolStatusMark } from "@/features/chat/components/ToolStatusMark";
import { CHAT_TEXTS } from "@/features/chat/texts";
import type { ToolCall, ToolField } from "@/features/chat/types";

interface ToolRowProps {
  call: ToolCall;
  onShowAll: (call: ToolCall, field: ToolField) => void;
}

/** One tool call: its name, summary, and status. It opens to show the fields. */
export function ToolRow({ call, onShowAll }: ToolRowProps): React.JSX.Element {
  const [open, setOpen] = useState(call.status === "error");
  const panelId = `tool-${call.id}`;
  return (
    <Box component="li" sx={{ borderBottom: 1, borderColor: "divider", "&:last-child": { borderBottom: 0 } }}>
      <ButtonBase
        onClick={() => setOpen(!open)}
        aria-expanded={open}
        aria-controls={panelId}
        sx={{ display: "flex", width: "100%", gap: 1, px: 1.5, py: 0.5, minHeight: 44, textAlign: "left", alignItems: "center" }}
      >
        <span className="flex min-w-0 flex-1 flex-col">
          <Typography variant="caption" sx={{ fontFamily: "ui-monospace, Menlo, monospace", fontWeight: 700 }}>
            {call.name}
          </Typography>
          {call.summary ? (
            <Typography variant="caption" color="text.secondary" noWrap>
              {call.summary}
            </Typography>
          ) : null}
        </span>
        <ToolStatusMark status={call.status} />
      </ButtonBase>
      {open ? (
        <div id={panelId} className="flex flex-col gap-2 px-3 pb-3">
          {call.fields.length === 0 ? (
            <Typography variant="caption" color="text.secondary">
              {CHAT_TEXTS.tools.noDetails}
            </Typography>
          ) : (
            call.fields.map((field) => (
              <ToolFieldView key={field.key} field={field} onShowAll={(f) => onShowAll(call, f)} />
            ))
          )}
        </div>
      ) : null}
    </Box>
  );
}
