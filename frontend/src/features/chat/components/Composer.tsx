import SendIcon from "@mui/icons-material/Send";
import Box from "@mui/material/Box";
import IconButton from "@mui/material/IconButton";
import TextField from "@mui/material/TextField";
import { useState } from "react";

import { CHAT_TEXTS } from "@/features/chat/texts";

interface ComposerProps {
  /** True while a turn runs. Only the send action stops; the field stays open for a draft. */
  busy: boolean;
  onSend: (message: string) => void;
}

const MAX_ROWS = 5;

export function Composer({ busy, onSend }: ComposerProps): React.JSX.Element {
  const [text, setText] = useState("");
  const message = text.trim();

  const submit = (): void => {
    if (busy || message === "") return;
    onSend(message);
    setText("");
  };

  return (
    <Box
      component="form"
      sx={{ display: "flex", alignItems: "flex-end", gap: 1, p: 1.5, borderTop: 1, borderColor: "divider" }}
      onSubmit={(event) => {
        event.preventDefault();
        submit();
      }}
    >
      <TextField
        label={CHAT_TEXTS.composer.label}
        helperText={CHAT_TEXTS.composer.hint}
        value={text}
        onChange={(event) => setText(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            submit();
          }
        }}
        multiline
        maxRows={MAX_ROWS}
        size="small"
        fullWidth
      />
      <IconButton type="submit" color="primary" aria-label={CHAT_TEXTS.composer.send} disabled={busy || message === ""}>
        <SendIcon />
      </IconButton>
    </Box>
  );
}
