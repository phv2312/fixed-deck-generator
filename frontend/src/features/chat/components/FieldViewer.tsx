import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Typography from "@mui/material/Typography";
import { useEffect, useRef, useState } from "react";

import { isImage } from "@/features/chat/format";
import { useCopyField, useToolField } from "@/features/chat/queries";
import { CHAT_TEXTS } from "@/features/chat/texts";
import type { ToolField } from "@/features/chat/types";
import { apiUrl, errorText } from "@/shared/api";
import { LoadingState } from "@/shared/ui";

interface FieldViewerProps {
  title: string;
  field: ToolField;
  onClose: () => void;
}

/** The full value of one tool field. It covers the chat panel. Close with the button or Escape. */
export function FieldViewer({ title, field, onClose }: FieldViewerProps): React.JSX.Element {
  const value = useToolField(field.url, true);
  const copyField = useCopyField();
  const [copied, setCopied] = useState(false);
  const closeRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    closeRef.current?.focus();
    const onKey = (event: KeyboardEvent): void => {
      if (event.key === "Escape") onClose();
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [onClose]);

  return (
    <Box
      component="section"
      aria-label={CHAT_TEXTS.viewer.label(title)}
      sx={{ position: "absolute", inset: 0, zIndex: 1, display: "flex", flexDirection: "column", bgcolor: "background.paper" }}
    >
      <Box sx={{ display: "flex", flexWrap: "wrap", alignItems: "center", gap: 1, p: 1.5, borderBottom: 1, borderColor: "divider" }}>
        <Typography variant="body2" sx={{ fontWeight: 700, flex: 1, minWidth: 0, overflowWrap: "anywhere" }}>
          {title}
        </Typography>
        <Button size="small" variant="outlined" onClick={() => void copyField(field.url).then(() => setCopied(true))}>
          {copied ? CHAT_TEXTS.viewer.copied : CHAT_TEXTS.viewer.copy}
        </Button>
        <Button size="small" variant="outlined" component="a" href={apiUrl(field.url, { download: "true" })} download>
          {CHAT_TEXTS.viewer.download}
        </Button>
        <Button ref={closeRef} size="small" variant="contained" onClick={onClose}>
          {CHAT_TEXTS.viewer.close}
        </Button>
      </Box>
      <div className="flex min-h-0 flex-1 flex-col gap-3 overflow-auto p-3">
        {isImage(field.mime) ? (
          <Box
            component="img"
            src={apiUrl(field.url)}
            alt={CHAT_TEXTS.field.previewAlt(field.key)}
            sx={{ maxWidth: "100%", maxHeight: 240, objectFit: "contain", alignSelf: "flex-start", border: 1, borderColor: "divider", borderRadius: 1 }}
          />
        ) : null}
        {value.isPending ? <LoadingState /> : null}
        {value.isError ? <Alert severity="error">{errorText(value.error)}</Alert> : null}
        {value.data !== undefined ? (
          <Box
            component="pre"
            sx={{ m: 0, fontFamily: "ui-monospace, Menlo, monospace", fontSize: "0.75rem", lineHeight: 1.5, whiteSpace: "pre-wrap", wordBreak: "break-all" }}
          >
            {value.data}
          </Box>
        ) : null}
      </div>
    </Box>
  );
}
