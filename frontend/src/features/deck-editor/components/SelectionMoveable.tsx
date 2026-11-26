import Moveable, { type OnDragEnd, type OnResizeEnd } from "react-moveable";

import { MIN_ELEMENT_SIZE, SNAP_THRESHOLD } from "@/features/deck-editor/constants";
import { boxChanges, canMove, canResize, moveChanges } from "@/features/deck-editor/geometry";
import type { DeckElement } from "@/features/deck-editor/types";

interface SelectionMoveableProps {
  target: HTMLElement;
  element: DeckElement;
  scale: number;
  onChange: (changes: Record<string, unknown>) => void;
  onGesture: (active: boolean) => void;
}

function clearStyle(target: HTMLElement | SVGElement): void {
  target.style.transform = "";
}

/** Handles to drag and resize the selected element. Each gesture ends in one saved edit. */
export function SelectionMoveable({ target, element, scale, onChange, onGesture }: SelectionMoveableProps): React.JSX.Element {
  const finishDrag = (event: OnDragEnd): void => {
    onGesture(false);
    clearStyle(event.target);
    const [tx = 0, ty = 0] = event.lastEvent?.beforeTranslate ?? [];
    if (event.isDrag && (tx !== 0 || ty !== 0)) onChange(moveChanges(element, tx / scale, ty / scale));
  };
  const finishResize = (event: OnResizeEnd): void => {
    onGesture(false);
    clearStyle(event.target);
    const last = event.lastEvent;
    if (!event.isDrag || !last) return;
    const [tx = 0, ty = 0] = last.drag.beforeTranslate;
    onChange(boxChanges({ x: element.x + tx / scale, y: element.y + ty / scale, w: last.width / scale, h: last.height / scale }));
  };
  return (
    <Moveable
      target={target}
      draggable={canMove(element)}
      resizable={canResize(element)}
      origin={false}
      snappable
      snapThreshold={SNAP_THRESHOLD}
      elementGuidelines={['[data-deck-box]:not([data-selected])']}
      snapDirections={{ left: true, top: true, right: true, bottom: true, center: true, middle: true }}
      elementSnapDirections={{ left: true, top: true, right: true, bottom: true, center: true, middle: true }}
      isDisplaySnapDigit={false}
      throttleDrag={0}
      throttleResize={0}
      renderDirections={["nw", "n", "ne", "w", "e", "sw", "s", "se"]}
      onDrag={(event) => {
        onGesture(true);
        event.target.style.transform = event.transform;
      }}
      onDragEnd={finishDrag}
      onResize={(event) => {
        onGesture(true);
        event.target.style.width = `${Math.max(event.width, MIN_ELEMENT_SIZE * scale)}px`;
        event.target.style.height = `${Math.max(event.height, MIN_ELEMENT_SIZE * scale)}px`;
        event.target.style.transform = event.drag.transform;
      }}
      onResizeEnd={finishResize}
    />
  );
}
