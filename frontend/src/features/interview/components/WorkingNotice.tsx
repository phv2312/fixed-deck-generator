import CircularProgress from "@mui/material/CircularProgress";
import Typography from "@mui/material/Typography";

import { INTERVIEW_TEXTS } from "@/features/interview/texts";

/** Shown while the assistant works and there is no question or plan to show yet. */
export function WorkingNotice(): React.JSX.Element {
  return (
    <div role="status" className="flex flex-col items-center gap-2 py-12 text-center">
      <CircularProgress aria-hidden size="2rem" />
      <Typography variant="h3" component="h2">
        {INTERVIEW_TEXTS.working.title}
      </Typography>
      <Typography color="text.secondary">{INTERVIEW_TEXTS.working.hint}</Typography>
    </div>
  );
}
