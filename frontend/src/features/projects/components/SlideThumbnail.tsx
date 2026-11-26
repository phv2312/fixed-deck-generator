import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import { useRef } from "react";

import { SLIDE_HEIGHT, SLIDE_WIDTH } from "@/features/projects/constants";
import { PROJECT_TEXTS } from "@/features/projects/texts";
import { useElementWidth } from "@/shared/hooks";

interface SlideThumbnailProps {
  name: string;
  url: string | null;
}

/** Show the first slide. The slide is HTML of the backend, scaled to fit the card. */
export function SlideThumbnail({ name, url }: SlideThumbnailProps): React.JSX.Element {
  const ref = useRef<HTMLDivElement>(null);
  const width = useElementWidth(ref);
  return (
    <Box
      ref={ref}
      className="relative aspect-video w-full overflow-hidden"
      sx={{ bgcolor: "action.hover", borderBottom: 1, borderColor: "divider" }}
    >
      {url ? (
        <iframe
          title={PROJECT_TEXTS.thumbnailTitle(name)}
          src={url}
          sandbox=""
          loading="lazy"
          tabIndex={-1}
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            border: 0,
            pointerEvents: "none",
            width: SLIDE_WIDTH,
            height: SLIDE_HEIGHT,
            transform: `scale(${width / SLIDE_WIDTH})`,
            transformOrigin: "top left",
          }}
        />
      ) : (
        <Typography color="text.secondary" variant="body2" className="absolute inset-0 grid place-items-center">
          {PROJECT_TEXTS.noThumbnail}
        </Typography>
      )}
    </Box>
  );
}
