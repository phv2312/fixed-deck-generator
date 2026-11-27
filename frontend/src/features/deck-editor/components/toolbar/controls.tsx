import FormatAlignCenter from "@mui/icons-material/FormatAlignCenter";
import FormatAlignLeft from "@mui/icons-material/FormatAlignLeft";
import FormatAlignRight from "@mui/icons-material/FormatAlignRight";
import EditOutlined from "@mui/icons-material/EditOutlined";
import FormatBold from "@mui/icons-material/FormatBold";
import FormatItalic from "@mui/icons-material/FormatItalic";
import FormatUnderlined from "@mui/icons-material/FormatUnderlined";
import Button from "@mui/material/Button";

import { ChoiceSelect, FontSizeMenu, IconToggle, PresetSelect, TokenSelect } from "@/features/deck-editor/components/toolbar/fields";
import { SIZE_PRESETS } from "@/features/deck-editor/constants";
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

function Size({ element, patch, field, label }: Pick<ControlsProps, "element" | "patch"> & {
  field: keyof typeof SIZE_PRESETS; label: string;
}): React.JSX.Element | null {
  if (!can(element, field)) return null;
  return <PresetSelect label={label} value={element.props[field]} presets={SIZE_PRESETS[field]} onChange={(value) => patch({ [field]: value })} />;
}

function FontSize({ element, patch }: Pick<ControlsProps, "element" | "patch">): React.JSX.Element | null {
  if (!can(element, "font_size")) return null;
  return <FontSizeMenu value={element.props.font_size} onChange={(size) => patch({ font_size: size })} />;
}

function Align({ element, patch }: Pick<ControlsProps, "element" | "patch">): React.JSX.Element | null {
  if (!can(element, "align")) return null;
  const left = { value: "left", label: T.alignLeft, icon: <FormatAlignLeft fontSize="small" /> };
  const items = [
    left,
    { value: "center", label: T.alignCenter, icon: <FormatAlignCenter fontSize="small" /> },
    { value: "right", label: T.alignRight, icon: <FormatAlignRight fontSize="small" /> },
  ];
  const at = Math.max(0, items.findIndex((item) => item.value === element.props.align));
  const current = items[at] ?? left;
  const next = items[(at + 1) % items.length] ?? current;
  return (
    <IconToggle label={current.label} selected={false} onToggle={() => patch({ align: next.value })}>
      {current.icon}
    </IconToggle>
  );
}

function TextControls(props: ControlsProps): React.JSX.Element {
  const { element, patch, editText } = props;
  return (
    <>
      <FontSize element={element} patch={patch} />
      <Toggle element={element} patch={patch} field="bold" label={T.bold}><FormatBold fontSize="small" /></Toggle>
      <Toggle element={element} patch={patch} field="italic" label={T.italic}><FormatItalic fontSize="small" /></Toggle>
      <Toggle element={element} patch={patch} field="underline" label={T.underline}><FormatUnderlined fontSize="small" /></Toggle>
      <Align element={element} patch={patch} />
      <Token element={element} patch={patch} field="color" label={T.color} />
      <IconToggle label={T.editText} selected={false} onToggle={editText}><EditOutlined fontSize="small" /></IconToggle>
    </>
  );
}

function ShapeControls({ element, patch }: ControlsProps): React.JSX.Element {
  const kind = typeof element.props.shape === "string" ? element.props.shape : "rect";
  return (
    <>
      <Token element={element} patch={patch} field="fill" label={T.fill} none />
      <Token element={element} patch={patch} field="stroke" label={T.stroke} none />
      <Size element={element} patch={patch} field="stroke_width" label={T.strokeWidth} />
      {can(element, "shape") && (
        <ChoiceSelect label={T.shape} value={kind} onChange={(shape) => patch({ shape })}
          options={[{ value: "rect", text: T.rect }, { value: "ellipse", text: T.ellipse }]} />
      )}
      {kind === "rect" && <Size element={element} patch={patch} field="radius" label={T.radius} />}
    </>
  );
}

function LineControls({ element, patch }: ControlsProps): React.JSX.Element {
  return (
    <>
      <Token element={element} patch={patch} field="color" label={T.color} />
      <Size element={element} patch={patch} field="width" label={T.strokeWidth} />
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
      {can(element, "src") && <Button size="small" color="inherit" onClick={() => openDialog("image")}>{T.editImage}</Button>}
    </>
  );
}

function TableControls({ element, patch, openDialog }: ControlsProps): React.JSX.Element {
  return (
    <>
      <Toggle element={element} patch={patch} field="header" label={T.header}><span aria-hidden="true">H</span></Toggle>
      <FontSize element={element} patch={patch} />
      <Button size="small" color="inherit" onClick={() => openDialog("cells")}>{T.editCells}</Button>
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
      <Button size="small" color="inherit" onClick={() => openDialog("data")}>{T.editData}</Button>
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
