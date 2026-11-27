import CircularProgress from "@mui/material/CircularProgress";
import Typography from "@mui/material/Typography";

import { SHARED_TEXTS } from "@/shared/texts";

export function LoadingState(): React.JSX.Element {
  return (
    <div role="status" className="flex flex-col items-center gap-4 py-12">
      <CircularProgress aria-hidden size="2rem" />
      <Typography color="text.secondary">{SHARED_TEXTS.loading}</Typography>
    </div>
  );
}
