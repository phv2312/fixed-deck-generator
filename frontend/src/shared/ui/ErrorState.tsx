import Alert from "@mui/material/Alert";
import AlertTitle from "@mui/material/AlertTitle";
import Button from "@mui/material/Button";

import { errorText } from "@/shared/api";
import { SHARED_TEXTS } from "@/shared/texts";

interface ErrorStateProps {
  error: unknown;
  onRetry?: () => void;
}

export function ErrorState({ error, onRetry }: ErrorStateProps): React.JSX.Element {
  return (
    <Alert
      severity="error"
      action={
        onRetry ? (
          <Button color="inherit" onClick={onRetry}>
            {SHARED_TEXTS.retry}
          </Button>
        ) : undefined
      }
    >
      <AlertTitle>{SHARED_TEXTS.error.title}</AlertTitle>
      {errorText(error)}
    </Alert>
  );
}
