import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";

import { slideUrl } from "@/features/deck-editor/api";
import { EDITOR_TEXTS } from "@/features/deck-editor/texts";
import type { Deck, DeckSlide } from "@/features/deck-editor/types";
import { ScaledFrame } from "@/shared/ui";

interface ThumbProps {
  projectId: string;
  deck: Deck;
  slide: DeckSlide;
  current: boolean;
  onPick: () => void;
}

function Thumb({ projectId, deck, slide, current, onPick }: ThumbProps): React.JSX.Element {
  const label = EDITOR_TEXTS.slideLabel(slide.index + 1, slide.title);
  return (
    <Box
      component="button"
      type="button"
      onClick={onPick}
      aria-label={label}
      aria-current={current ? "true" : undefined}
      sx={{ display: "flex", alignItems: "flex-start", gap: 1, p: 0, flex: "none", cursor: "pointer",
        bgcolor: "transparent", border: 0, width: { xs: "10rem", md: "100%" },
        "&:hover > div": { borderColor: "primary.light" } }}
    >
      <Typography variant="caption" color="text.secondary" component="span" sx={{ minWidth: 16 }}>
        {slide.index + 1}
      </Typography>
      <Box sx={{ flex: 1, borderStyle: "solid", borderWidth: current ? 2 : 1, borderColor: current ? "primary.main" : "divider", bgcolor: "background.paper" }}>
        <ScaledFrame src={slideUrl(projectId, deck, slide)} title={label} width={deck.width} height={deck.height} lazy />
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
        <Thumb key={slide.id} projectId={projectId} deck={deck} slide={slide}
          current={slide.index === current} onPick={() => onPick(slide.index)} />
      ))}
    </nav>
  );
}
