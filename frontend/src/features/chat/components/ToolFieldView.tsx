import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Typography from "@mui/material/Typography";
import { useState } from "react";

import { formatBytes, isImage } from "@/features/chat/format";
import { useCopyField } from "@/features/chat/queries";
import { CHAT_TEXTS } from "@/features/chat/texts";
import type { ToolField } from "@/features/chat/types";
import { apiUrl } from "@/shared/api";

const PREVIEW_LINES = 3;

interface ToolFieldViewProps {
  field: ToolField;
  onShowAll: (field: ToolField) => void;
}

/** One input or output of a tool call: a short preview, never the full value. */
export function ToolFieldView({ field, onShowAll }: ToolFieldViewProps): React.JSX.Element {
  const copyField = useCopyField();
  const [copied, setCopied] = useState(false);

  const copy = (): void => {
    void copyField(field.url).then(() => setCopied(true));
  };

  return (
    <div className="flex flex-col gap-1">
      <div className="flex justify-between gap-2">
        <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600 }}>
          {field.key}
        </Typography>
        <Typography variant="caption" color="text.secondary">
          {CHAT_TEXTS.field.meta(formatBytes(field.size), field.mime)}
        </Typography>
      </div>
      {isImage(field.mime) ? (
        <Box
          component="img"
          src={apiUrl(field.url)}
          alt={CHAT_TEXTS.field.previewAlt(field.key)}
          sx={{ maxHeight: 96, maxWidth: "100%", objectFit: "contain", alignSelf: "flex-start", bgcolor: "background.paper", border: 1, borderColor: "divider", borderRadius: 1 }}
        />
      ) : (
        <Typography
          variant="caption"
          component="div"
          sx={{
            fontFamily: "ui-monospace, Menlo, monospace",
            wordBreak: "break-all",
            display: "-webkit-box",
            WebkitLineClamp: PREVIEW_LINES,
            WebkitBoxOrient: "vertical",
            overflow: "hidden",
          }}
        >
          {field.preview}
        </Typography>
      )}
      <div className="flex gap-1">
        <Button size="small" variant="outlined" onClick={() => onShowAll(field)}>
          {CHAT_TEXTS.field.showAll}
        </Button>
        <Button size="small" variant="outlined" onClick={copy}>
          {copied ? CHAT_TEXTS.field.copied : CHAT_TEXTS.field.copy}
        </Button>
      </div>
    </div>
  );
}
