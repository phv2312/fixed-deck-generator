import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";

import { SLIDE_HEIGHT, SLIDE_WIDTH } from "@/features/projects/constants";
import { PROJECT_TEXTS } from "@/features/projects/texts";
import { ScaledFrame } from "@/shared/ui";

interface SlideThumbnailProps {
  name: string;
  url: string | null;
}

/** Show the first slide. The slide is HTML of the backend, scaled to fit the card. */
export function SlideThumbnail({ name, url }: SlideThumbnailProps): React.JSX.Element {
  return (
    <Box className="relative aspect-video w-full overflow-hidden" sx={{ bgcolor: "action.hover", borderBottom: 1, borderColor: "divider" }}>
      {url ? (
        <ScaledFrame src={url} title={PROJECT_TEXTS.thumbnailTitle(name)} width={SLIDE_WIDTH} height={SLIDE_HEIGHT} lazy />
      ) : (
        <Typography color="text.secondary" variant="body2" className="absolute inset-0 grid place-items-center">
          {PROJECT_TEXTS.noThumbnail}
        </Typography>
      )}
    </Box>
  );
}
