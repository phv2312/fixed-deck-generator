import Box from "@mui/material/Box";
import useMediaQuery from "@mui/material/useMediaQuery";
import Typography from "@mui/material/Typography";
import { useRef, useState } from "react";

import { slideUrl } from "@/features/deck-editor/api";
import { ElementBoxes } from "@/features/deck-editor/components/ElementBoxes";
import { SelectionMoveable } from "@/features/deck-editor/components/SelectionMoveable";
import { TextEditor } from "@/features/deck-editor/components/TextEditor";
import { ElementToolbar } from "@/features/deck-editor/components/toolbar/ElementToolbar";
import type { DeckEditorState } from "@/features/deck-editor/hooks/useDeckEditor";
import { EDITOR_TEXTS } from "@/features/deck-editor/texts";
import type { Deck, DeckSlide } from "@/features/deck-editor/types";
import { useElementWidth } from "@/shared/hooks";
import { ScaledFrame } from "@/shared/ui";

interface SlideStageProps {
  projectId: string;
  deck: Deck;
  slide: DeckSlide;
  editor: DeckEditorState;
}

/** The slide as the backend renders it, with the boxes of the elements on top. */
export function SlideStage({ projectId, deck, slide, editor }: SlideStageProps): React.JSX.Element {
  const ref = useRef<HTMLDivElement>(null);
  const width = useElementWidth(ref);
  const scale = width / deck.width;
  const [target, setTarget] = useState<HTMLElement | null>(null);
  const [gesture, setGesture] = useState(false);
  const [modal, setModal] = useState(false);
  const docked = useMediaQuery((theme) => theme.breakpoints.down("lg"));
  const { selected, editingText, locked } = editor;
  const ready = selected !== undefined && target !== null && width > 0;
  const toolbar = (floating: boolean): React.JSX.Element | null =>
    ready && floating === !docked ? (
      <ElementToolbar element={selected} target={target} editor={editor} hidden={gesture || editingText} docked={docked} onModal={setModal} />
    ) : null;
  return (
    <div className="flex flex-col gap-2">
      <Box
        ref={ref}
        role="group"
        aria-label={EDITOR_TEXTS.stageLabel}
        sx={{ position: "relative", width: "100%", aspectRatio: "16 / 9", border: 1, borderColor: "divider",
          bgcolor: "background.paper", boxShadow: 1,
          "& .moveable-control-box": { "--moveable-color": (theme) => theme.palette.primary.main } }}
      >
        <Box sx={{ position: "absolute", inset: 0, overflow: "hidden" }}>
          <ScaledFrame src={slideUrl(projectId, deck, slide)} width={deck.width} height={deck.height}
            title={EDITOR_TEXTS.slideLabel(slide.index + 1, slide.title)} />
        </Box>
        {!locked && <ElementBoxes elements={slide.elements} scale={scale} editor={editor} onSelectedNode={setTarget} frozen={gesture} />}
        {ready && !editingText && !modal && (
          <SelectionMoveable target={target} element={selected} scale={scale} onChange={editor.patch} onGesture={setGesture} />
        )}
        {toolbar(true)}
        {ready && editingText && (
          <TextEditor element={selected} scale={scale}
            onCommit={(text) => {
              editor.stopTextEdit();
              target.focus();
              if (text !== selected.props.text) editor.patch({ text });
            }}
            onCancel={() => {
              editor.stopTextEdit();
              target.focus();
            }} />
        )}
      </Box>
      {toolbar(false)}
      {!locked && <Typography variant="caption" color="text.secondary">{EDITOR_TEXTS.stageHint}</Typography>}
    </div>
  );
}
