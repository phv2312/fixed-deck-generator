import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import { useRef } from "react";

import { slideHtmlUrl } from "@/features/deck-editor/api";
import { SlideFrame } from "@/features/deck-editor/components/SlideFrame";
import { CANVAS_WIDTH } from "@/features/deck-editor/constants";
import { EDITOR_TEXTS } from "@/features/deck-editor/texts";
import type { Deck, DeckSlide } from "@/features/deck-editor/types";
import { useElementWidth } from "@/shared/hooks";

interface ThumbProps {
  projectId: string;
  slide: DeckSlide;
  revision: number;
  current: boolean;
  onPick: () => void;
}

function Thumb({ projectId, slide, revision, current, onPick }: ThumbProps): React.JSX.Element {
  const ref = useRef<HTMLDivElement>(null);
  const width = useElementWidth(ref);
  const label = EDITOR_TEXTS.slideLabel(slide.index + 1, slide.title);
  return (
    <Box
      component="button"
      type="button"
      onClick={onPick}
      aria-label={label}
      aria-current={current ? "true" : undefined}
      sx={{ display: "flex", alignItems: "flex-start", gap: 1, p: 0.5, flex: "none", cursor: "pointer",
        bgcolor: "transparent", border: 2, borderRadius: 1, borderColor: current ? "primary.main" : "transparent",
        width: { xs: "10rem", md: "100%" }, "&:hover": { borderColor: "primary.light" } }}
    >
      <Typography variant="caption" color="text.secondary" component="span" sx={{ minWidth: 16 }}>
        {slide.index + 1}
      </Typography>
      <Box ref={ref} sx={{ position: "relative", flex: 1, aspectRatio: "16 / 9", overflow: "hidden",
        border: 1, borderColor: "divider", bgcolor: "background.paper" }}>
        <SlideFrame src={slideHtmlUrl(projectId, slide.index, revision)} title={label} scale={width / CANVAS_WIDTH} />
      </Box>
    </Box>
  );
}

interface SlideListProps {
  projectId: string;
  deck: Deck;
  current: number;
  onPick: (index: number) => void;
}

/** The slides in a column, or in a row on a narrow screen. Click one to edit it. */
export function SlideList({ projectId, deck, current, onPick }: SlideListProps): React.JSX.Element {
  return (
    <nav aria-label={EDITOR_TEXTS.slides} className="flex gap-2 overflow-auto md:w-48 md:flex-none md:flex-col md:pr-1 md:max-h-[80vh]">
      {deck.slides.map((slide) => (
        <Thumb key={slide.id} projectId={projectId} slide={slide} revision={deck.revision}
          current={slide.index === current} onPick={() => onPick(slide.index)} />
      ))}
    </nav>
  );
}
