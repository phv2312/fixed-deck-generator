import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";

import { INTERVIEW_TEXTS } from "@/features/interview/texts";
import type { PlanSlide } from "@/features/interview/types";

/** The planned slides in order. The order is real, so the list is numbered. */
export function PlanSlideList({ slides }: { slides: PlanSlide[] }): React.JSX.Element {
  return (
    <Box
      component="ol"
      sx={{ m: 0, p: 0, listStyle: "none", border: 1, borderColor: "divider", borderRadius: 1, bgcolor: "background.paper" }}
    >
      {slides.map((slide, position) => (
        <Box
          component="li"
          key={slide.id}
          sx={{ display: "flex", gap: 2, p: 2, borderBottom: 1, borderColor: "divider", "&:last-child": { borderBottom: 0 } }}
        >
          <Typography color="text.secondary" sx={{ width: 24, flexShrink: 0 }}>
            {position + 1}
          </Typography>
          <div className="flex min-w-0 flex-1 flex-col gap-1">
            <div className="flex flex-wrap justify-between gap-2">
              <Typography sx={{ fontWeight: 600 }}>{slide.title}</Typography>
              <Typography variant="caption" color="text.secondary">
                {slide.kind ?? INTERVIEW_TEXTS.plan.kindUnknown}
              </Typography>
            </div>
            <Typography variant="body2" color="text.secondary">
              {slide.summary || slide.purpose || INTERVIEW_TEXTS.plan.noSummary}
            </Typography>
            {slide.points.length > 0 ? (
              <Box component="ul" sx={{ m: 0, pl: 3, typography: "body2" }}>
                {slide.points.map((point) => (
                  <li key={point}>{point}</li>
                ))}
              </Box>
            ) : null}
          </div>
        </Box>
      ))}
    </Box>
  );
}
