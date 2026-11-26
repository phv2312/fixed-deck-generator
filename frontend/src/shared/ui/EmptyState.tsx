import Button from "@mui/material/Button";
import Typography from "@mui/material/Typography";

interface EmptyStateProps {
  title: string;
  hint: string;
  actionLabel?: string;
  onAction?: () => void;
}

export function EmptyState({ title, hint, actionLabel, onAction }: EmptyStateProps): React.JSX.Element {
  return (
    <div className="flex flex-col items-center gap-2 py-12 text-center">
      <Typography variant="h3" component="h2">
        {title}
      </Typography>
      <Typography color="text.secondary">{hint}</Typography>
      {actionLabel && onAction ? (
        <Button variant="contained" onClick={onAction}>
          {actionLabel}
        </Button>
      ) : null}
    </div>
  );
}
