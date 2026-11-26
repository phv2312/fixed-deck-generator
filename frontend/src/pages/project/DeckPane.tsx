import LinearProgress from "@mui/material/LinearProgress";
import Typography from "@mui/material/Typography";

import { DeckEditor } from "@/features/deck-editor";
import type { Phase } from "@/features/projects";
import { PAGE_TEXTS } from "@/pages/texts";

interface DeckPaneProps {
  projectId: string;
  phase: Phase;
  progress: { index: number; total: number } | null;
}

/** Placeholder for the deck editor. It shows the state of the build. */
export function DeckPane({ projectId, phase, progress }: DeckPaneProps): React.JSX.Element {
  const texts = PAGE_TEXTS.deck;
  if (phase === "generated") return <DeckEditor projectId={projectId} />;
  if (phase === "approved") {
    return (
      <div className="mx-auto flex max-w-xl flex-col gap-2 py-12 text-center">
        <Typography variant="h2">{texts.approved.title}</Typography>
        <Typography color="text.secondary">{texts.approved.hint}</Typography>
      </div>
    );
  }
  const value = progress && progress.total > 0 ? (progress.index / progress.total) * 100 : undefined;
  return (
    <div className="mx-auto flex w-full max-w-xl flex-col gap-4 py-12">
      <Typography variant="h2">{texts.generating.title}</Typography>
      <LinearProgress
        variant={value === undefined ? "indeterminate" : "determinate"}
        value={value}
        aria-label={texts.generating.title}
      />
      <Typography color="text.secondary" role="status">
        {progress ? texts.generating.progress(progress.index, progress.total) : texts.working}
      </Typography>
    </div>
  );
}
