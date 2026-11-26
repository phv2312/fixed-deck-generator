import Box from "@mui/material/Box";
import NativeSelect from "@mui/material/NativeSelect";
import TextField from "@mui/material/TextField";
import ToggleButton from "@mui/material/ToggleButton";
import Typography from "@mui/material/Typography";
import { useState } from "react";

import { COLOR_TOKENS } from "@/features/deck-editor/constants";
import { EDITOR_TEXTS } from "@/features/deck-editor/texts";

interface LabeledProps {
  label: string;
  children: React.ReactNode;
}

/** A field with its name shown beside it. The name is also its accessible name. */
function Labeled({ label, children }: LabeledProps): React.JSX.Element {
  return (
    <Box component="label" sx={{ display: "inline-flex", alignItems: "center", gap: 0.5 }}>
      <Typography variant="caption" color="text.secondary" component="span">{label}</Typography>
      {children}
    </Box>
  );
}

interface IconToggleProps {
  label: string;
  selected: boolean;
  onToggle: () => void;
  children: React.ReactNode;
}

/** A button that is on or off. It has a name for a screen reader. */
export function IconToggle({ label, selected, onToggle, children }: IconToggleProps): React.JSX.Element {
  return (
    <ToggleButton
      value={label}
      aria-label={label}
      title={label}
      size="small"
      selected={selected}
      onChange={onToggle}
      sx={{ border: 0 }}
    >
      {children}
    </ToggleButton>
  );
}

interface ChoiceSelectProps {
  label: string;
  value: string;
  options: readonly { value: string; text: string }[];
  onChange: (value: string) => void;
}

export function ChoiceSelect({ label, value, options, onChange }: ChoiceSelectProps): React.JSX.Element {
  return (
    <Labeled label={label}>
      <NativeSelect value={value} onChange={(event) => onChange(event.target.value)} inputProps={{ "aria-label": label }}>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.text}
          </option>
        ))}
      </NativeSelect>
    </Labeled>
  );
}

interface TokenSelectProps {
  label: string;
  value: unknown;
  onChange: (value: string | null) => void;
  allowNone?: boolean;
}

const NONE = "__none__";

/** Choose one color token of the deck theme. A hex color from the agent stays as it is. */
export function TokenSelect({ label, value, onChange, allowNone }: TokenSelectProps): React.JSX.Element {
  const current = typeof value === "string" ? value : NONE;
  const known: readonly string[] = COLOR_TOKENS;
  const options = [
    ...(allowNone ? [{ value: NONE, text: EDITOR_TEXTS.toolbar.none }] : []),
    ...(current !== NONE && !known.includes(current) ? [{ value: current, text: current }] : []),
    ...COLOR_TOKENS.map((token) => ({ value: token, text: token })),
  ];
  return (
    <ChoiceSelect
      label={label}
      value={current}
      options={options}
      onChange={(next) => onChange(next === NONE ? null : next)}
    />
  );
}

interface NumberFieldProps {
  label: string;
  value: unknown;
  min?: number;
  onCommit: (value: number) => void;
}

/** A number box. It saves when the user leaves it or presses Enter. */
export function NumberField({ label, value, min = 0, onCommit }: NumberFieldProps): React.JSX.Element {
  const shown = typeof value === "number" ? String(Math.round(value * 10) / 10) : "";
  const [draft, setDraft] = useState<string | null>(null);
  const commit = (): void => {
    const next = Number(draft);
    if (draft !== null && draft !== "" && Number.isFinite(next) && next >= min && next !== Number(shown)) onCommit(next);
    setDraft(null);
  };
  return (
    <Labeled label={label}>
    <TextField
      type="number"
      size="small"
      value={draft ?? shown}
      onChange={(event) => setDraft(event.target.value)}
      onBlur={commit}
      onKeyDown={(event) => {
        if (event.key === "Enter") commit();
      }}
      slotProps={{ htmlInput: { "aria-label": label, min } }}
      sx={{ width: (theme) => theme.spacing(10) }}
    />
    </Labeled>
  );
}
