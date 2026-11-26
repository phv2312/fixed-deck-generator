import FormatAlignCenter from "@mui/icons-material/FormatAlignCenter";
import FormatAlignLeft from "@mui/icons-material/FormatAlignLeft";
import FormatAlignRight from "@mui/icons-material/FormatAlignRight";
import FormatBold from "@mui/icons-material/FormatBold";
import FormatItalic from "@mui/icons-material/FormatItalic";
import FormatUnderlined from "@mui/icons-material/FormatUnderlined";
import Button from "@mui/material/Button";

import { ChoiceSelect, IconToggle, NumberField, TokenSelect } from "@/features/deck-editor/components/toolbar/fields";
import { EDITOR_TEXTS } from "@/features/deck-editor/texts";
import type { DeckElement } from "@/features/deck-editor/types";

const T = EDITOR_TEXTS.toolbar;

export interface ControlsProps {
  element: DeckElement;
  patch: (changes: Record<string, unknown>) => void;
  openDialog: (name: "cells" | "data" | "image") => void;
  editText: () => void;
}

const can = (element: DeckElement, field: string): boolean => element.editable.includes(field);

function Toggle({ element, patch, field, label, children }: Pick<ControlsProps, "element" | "patch"> & {
  field: string; label: string; children: React.ReactNode;
}): React.JSX.Element | null {
  if (!can(element, field)) return null;
  return (
    <IconToggle label={label} selected={element.props[field] === true} onToggle={() => patch({ [field]: element.props[field] !== true })}>
      {children}
    </IconToggle>
  );
}

function Token({ element, patch, field, label, none }: Pick<ControlsProps, "element" | "patch"> & {
  field: string; label: string; none?: boolean;
}): React.JSX.Element | null {
  if (!can(element, field)) return null;
  return <TokenSelect label={label} value={element.props[field]} allowNone={none} onChange={(value) => patch({ [field]: value })} />;
}

function Num({ element, patch, field, label, min }: Pick<ControlsProps, "element" | "patch"> & {
  field: string; label: string; min?: number;
}): React.JSX.Element | null {
  if (!can(element, field)) return null;
  return <NumberField label={label} value={element.props[field]} min={min} onCommit={(value) => patch({ [field]: value })} />;
}

function Align({ element, patch }: Pick<ControlsProps, "element" | "patch">): React.JSX.Element | null {
  if (!can(element, "align")) return null;
  const current = element.props.align;
  const items = [
    { value: "left", label: T.alignLeft, icon: <FormatAlignLeft fontSize="small" /> },
    { value: "center", label: T.alignCenter, icon: <FormatAlignCenter fontSize="small" /> },
    { value: "right", label: T.alignRight, icon: <FormatAlignRight fontSize="small" /> },
  ];
  return (
    <>
      {items.map((item) => (
        <IconToggle key={item.value} label={item.label} selected={current === item.value} onToggle={() => patch({ align: item.value })}>
          {item.icon}
        </IconToggle>
      ))}
    </>
  );
}

function TextControls(props: ControlsProps): React.JSX.Element {
  const { element, patch, editText } = props;
  return (
    <>
      <Num element={element} patch={patch} field="font_size" label={T.fontSize} min={1} />
      <Toggle element={element} patch={patch} field="bold" label={T.bold}><FormatBold fontSize="small" /></Toggle>
      <Toggle element={element} patch={patch} field="italic" label={T.italic}><FormatItalic fontSize="small" /></Toggle>
      <Toggle element={element} patch={patch} field="underline" label={T.underline}><FormatUnderlined fontSize="small" /></Toggle>
      <Align element={element} patch={patch} />
      <Token element={element} patch={patch} field="color" label={T.color} />
      <Button size="small" onClick={editText} sx={{ minHeight: 40 }}>{T.editText}</Button>
    </>
  );
}

function ShapeControls({ element, patch }: ControlsProps): React.JSX.Element {
  const kind = typeof element.props.shape === "string" ? element.props.shape : "rect";
  return (
    <>
      <Token element={element} patch={patch} field="fill" label={T.fill} none />
      <Token element={element} patch={patch} field="stroke" label={T.stroke} none />
      <Num element={element} patch={patch} field="stroke_width" label={T.strokeWidth} />
      {can(element, "shape") && (
        <ChoiceSelect label={T.shape} value={kind} onChange={(shape) => patch({ shape })}
          options={[{ value: "rect", text: T.rect }, { value: "ellipse", text: T.ellipse }]} />
      )}
      {kind === "rect" && <Num element={element} patch={patch} field="radius" label={T.radius} />}
    </>
  );
}

function LineControls({ element, patch }: ControlsProps): React.JSX.Element {
  return (
    <>
      <Token element={element} patch={patch} field="color" label={T.color} />
      <Num element={element} patch={patch} field="width" label={T.strokeWidth} />
      <Toggle element={element} patch={patch} field="dash" label={T.dash}><span aria-hidden="true">- -</span></Toggle>
      <Toggle element={element} patch={patch} field="arrow" label={T.arrow}><span aria-hidden="true">→</span></Toggle>
    </>
  );
}

function ImageControls({ element, patch, openDialog }: ControlsProps): React.JSX.Element {
  const fit = element.props.fit === "contain" ? "contain" : "cover";
  return (
    <>
      {can(element, "fit") && (
        <ChoiceSelect label={T.fit} value={fit} onChange={(next) => patch({ fit: next })}
          options={[{ value: "cover", text: T.cover }, { value: "contain", text: T.contain }]} />
      )}
      {can(element, "src") && <Button size="small" onClick={() => openDialog("image")} sx={{ minHeight: 40 }}>{T.editImage}</Button>}
    </>
  );
}

function TableControls({ element, patch, openDialog }: ControlsProps): React.JSX.Element {
  return (
    <>
      <Toggle element={element} patch={patch} field="header" label={T.header}><span aria-hidden="true">H</span></Toggle>
      <Num element={element} patch={patch} field="font_size" label={T.fontSize} min={1} />
      <Button size="small" onClick={() => openDialog("cells")} sx={{ minHeight: 40 }}>{T.editCells}</Button>
    </>
  );
}

function ChartControls({ element, patch, openDialog }: ControlsProps): React.JSX.Element {
  const kind = typeof element.props.kind === "string" ? element.props.kind : "bar";
  return (
    <>
      {can(element, "kind") && (
        <ChoiceSelect label={T.chartKind} value={kind} onChange={(next) => patch({ kind: next })}
          options={["bar", "line", "pie", "bubble"].map((v) => ({ value: v, text: v }))} />
      )}
      <Button size="small" onClick={() => openDialog("data")} sx={{ minHeight: 40 }}>{T.editData}</Button>
    </>
  );
}

const BY_TYPE: Partial<Record<DeckElement["type"], (props: ControlsProps) => React.JSX.Element>> = {
  text: TextControls, shape: ShapeControls, polygon: ShapeControls, line: LineControls,
  image: ImageControls, table: TableControls, chart: ChartControls,
};

/** The controls of one element type. Only fields in `editable` show. */
export function TypeControls(props: ControlsProps): React.JSX.Element | null {
  const Controls = BY_TYPE[props.element.type];
  return Controls ? <Controls {...props} /> : null;
}
