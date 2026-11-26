import { CANVAS_HEIGHT, CANVAS_WIDTH } from "@/features/deck-editor/constants";

interface SlideFrameProps {
  src: string;
  title: string;
  scale: number;
}

/** The HTML of the backend for one slide. It is scaled from the canvas size and ignores the mouse. */
export function SlideFrame({ src, title, scale }: SlideFrameProps): React.JSX.Element {
  return (
    <iframe
      title={title}
      src={src}
      sandbox=""
      tabIndex={-1}
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        border: 0,
        pointerEvents: "none",
        width: CANVAS_WIDTH,
        height: CANVAS_HEIGHT,
        transform: `scale(${scale})`,
        transformOrigin: "top left",
      }}
    />
  );
}
