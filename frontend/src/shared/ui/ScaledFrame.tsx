import Box from "@mui/material/Box";
import { useRef } from "react";

import { useElementWidth } from "@/shared/hooks";

interface ScaledFrameProps {
  src: string;
  title: string;
  /** Size of the page inside the frame, in its own units. The frame scales it to fit the width. */
  width: number;
  height: number;
  /** Load the page only when it comes near the screen. Use it for a long list. */
  lazy?: boolean;
}

/** A page of the backend, scaled to the width of its box. It ignores the mouse and the keyboard. */
export function ScaledFrame({ src, title, width, height, lazy = false }: ScaledFrameProps): React.JSX.Element {
  const ref = useRef<HTMLDivElement>(null);
  const scale = useElementWidth(ref) / width;
  return (
    <Box ref={ref} sx={{ position: "relative", width: "100%", aspectRatio: `${width} / ${height}`, overflow: "hidden" }}>
      <iframe
        title={title}
        src={src}
        sandbox=""
        loading={lazy ? "lazy" : "eager"}
        tabIndex={-1}
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          border: 0,
          pointerEvents: "none",
          width,
          height,
          transform: `scale(${scale})`,
          transformOrigin: "top left",
        }}
      />
    </Box>
  );
}
