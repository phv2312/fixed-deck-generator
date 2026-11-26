import Alert from "@mui/material/Alert";
import Button from "@mui/material/Button";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { useState } from "react";

import { PlanSlideList } from "@/features/interview/components/PlanSlideList";
import { INTERVIEW_TEXTS } from "@/features/interview/texts";
import type { Plan } from "@/features/interview/types";
import { ErrorState } from "@/shared/ui";

interface PlanReviewProps {
  plan: Plan;
  disabled: boolean;
  approving: boolean;
  approveError: unknown;
  onApprove: () => void;
  onRequestChanges: (text: string) => void;
}

function humanize(key: string): string {
  const words = key.replaceAll("_", " ");
  return words.charAt(0).toUpperCase() + words.slice(1);
}

function PlanFacts({ plan }: { plan: Plan }): React.JSX.Element {
  const facts = Object.entries(plan.meta);
  return (
    <div className="flex flex-col gap-2">
      <Typography variant="h3" component="h3">
        {INTERVIEW_TEXTS.plan.metaHeading}
      </Typography>
      <dl className="m-0 grid grid-cols-[auto_1fr] gap-x-4 gap-y-1">
        {[[INTERVIEW_TEXTS.plan.theme, plan.theme], ...facts.map(([key, value]) => [humanize(key), value])].map(([label, value]) => (
          <div key={label} className="contents">
            <Typography component="dt" variant="body2" color="text.secondary">
              {label}
            </Typography>
            <Typography component="dd" variant="body2" sx={{ m: 0 }}>
              {value}
            </Typography>
          </div>
        ))}
      </dl>
    </div>
  );
}

/** The plan to approve or to change. Open points are notes: they never block. */
export function PlanReview(props: PlanReviewProps): React.JSX.Element {
  const { plan, disabled, approving, approveError, onApprove, onRequestChanges } = props;
  const [changing, setChanging] = useState(false);
  const [text, setText] = useState("");
  const notes = [...(plan.missing.length > 0 ? [INTERVIEW_TEXTS.plan.missing(plan.missing)] : []), ...plan.variety];

  return (
    <div className="mx-auto flex w-full max-w-3xl flex-col gap-6">
      <div className="flex flex-col gap-1">
        <Typography variant="h2">{INTERVIEW_TEXTS.plan.heading}</Typography>
        <Typography color="text.secondary">{INTERVIEW_TEXTS.plan.summary(plan.slides.length)}</Typography>
      </div>
      <PlanFacts plan={plan} />
      <div className="flex flex-col gap-2">
        <Typography variant="h3" component="h3">
          {INTERVIEW_TEXTS.plan.slidesHeading}
        </Typography>
        <PlanSlideList slides={plan.slides} />
      </div>
      {notes.map((note) => (
        <Alert key={note} severity="info">
          {note}
        </Alert>
      ))}
      {approveError ? <ErrorState error={approveError} /> : null}
      {changing ? (
        <TextField
          label={INTERVIEW_TEXTS.plan.changesLabel}
          value={text}
          onChange={(event) => setText(event.target.value)}
          multiline
          minRows={3}
          fullWidth
        />
      ) : null}
      <div className="flex flex-wrap gap-4">
        <Button variant="contained" disabled={disabled || approving || !plan.can_approve} onClick={onApprove}>
          {approving ? INTERVIEW_TEXTS.plan.approving : INTERVIEW_TEXTS.plan.approve}
        </Button>
        {changing ? (
          <Button
            variant="outlined"
            disabled={disabled || text.trim() === ""}
            onClick={() => {
              onRequestChanges(text.trim());
              setText("");
              setChanging(false);
            }}
          >
            {INTERVIEW_TEXTS.plan.sendChanges}
          </Button>
        ) : null}
        <Button variant="outlined" disabled={disabled} onClick={() => setChanging(!changing)}>
          {changing ? INTERVIEW_TEXTS.plan.cancelChanges : INTERVIEW_TEXTS.plan.requestChanges}
        </Button>
      </div>
    </div>
  );
}
