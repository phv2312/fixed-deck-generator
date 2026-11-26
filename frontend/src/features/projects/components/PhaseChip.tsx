import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";

import { PROJECT_TEXTS } from "@/features/projects/texts";
import type { Phase } from "@/features/projects/types";

interface PhaseStyle {
  color: string;
  clipPath: string;
}

const CIRCLE = "circle(50%)";
const SQUARE = "inset(0)";
const TRIANGLE = "polygon(50% 0, 100% 100%, 0 100%)";
const DIAMOND = "polygon(50% 0, 100% 50%, 50% 100%, 0 50%)";

/** Each phase has its own shape, so the chip never relies on color alone. */
const PHASE_STYLES: Record<Phase, PhaseStyle> = {
  draft: { color: "text.secondary", clipPath: CIRCLE },
  interviewing: { color: "warning.main", clipPath: SQUARE },
  review: { color: "warning.main", clipPath: DIAMOND },
  approved: { color: "info.main", clipPath: SQUARE },
  generating: { color: "info.main", clipPath: TRIANGLE },
  generated: { color: "success.main", clipPath: CIRCLE },
};

/** While the assistant works the chip says so, whatever the phase is. */
export function PhaseChip({ phase, working = false }: { phase: Phase; working?: boolean }): React.JSX.Element {
  const style = working ? PHASE_STYLES.generating : PHASE_STYLES[phase];
  return (
    <div className="flex items-center gap-2">
      <Box
        aria-hidden
        sx={{ width: 8, height: 8, bgcolor: style.color, clipPath: style.clipPath, flexShrink: 0 }}
      />
      <Typography variant="caption" sx={{ color: style.color, fontWeight: 600 }}>
        {working ? PROJECT_TEXTS.working : PROJECT_TEXTS.phase[phase]}
      </Typography>
    </div>
  );
}
