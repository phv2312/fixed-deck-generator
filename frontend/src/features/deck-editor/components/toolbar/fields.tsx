import KeyboardArrowDown from "@mui/icons-material/KeyboardArrowDown";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Menu from "@mui/material/Menu";
import MenuItem from "@mui/material/MenuItem";
import NativeSelect from "@mui/material/NativeSelect";
import ToggleButton from "@mui/material/ToggleButton";
import Typography from "@mui/material/Typography";
import { useState } from "react";

import { COLOR_TOKENS, FONT_SIZES } from "@/features/deck-editor/constants";
import { EDITOR_TEXTS } from "@/features/deck-editor/texts";

interface LabeledProps {
  label: string;
  children: React.ReactNode;
}

/** A field in the compact toolbar. Its name is the hover title and the accessible name, not visible text. */
function Labeled({ label, children }: LabeledProps): React.JSX.Element {
  return <Box component="span" title={label} sx={{ display: "inline-flex", alignItems: "center" }}>{children}</Box>;
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

interface FontSizeMenuProps {
  value: unknown;
  onChange: (size: number) => void;
}

/** Choose a named text size, shown with its number. A size outside the list shows as "Custom". */
export function FontSizeMenu({ value, onChange }: FontSizeMenuProps): React.JSX.Element {
  const [anchor, setAnchor] = useState<HTMLElement | null>(null);
  const names = EDITOR_TEXTS.toolbar.fontSizes;
  const current = typeof value === "number" ? Math.round(value) : null;
  const named = FONT_SIZES.find((item) => item.size === current);
  const shown = named ? `${names[named.key]} · ${named.size}` : `${names.custom} · ${current ?? ""}`;
  const label = EDITOR_TEXTS.toolbar.fontSize;
  return (
    <>
      <Button size="small" color="inherit" aria-label={label} title={label} aria-haspopup="menu" aria-expanded={anchor !== null}
        endIcon={<KeyboardArrowDown fontSize="small" />} onClick={(event) => setAnchor(event.currentTarget)}>
        {shown}
      </Button>
      <Menu anchorEl={anchor} open={anchor !== null} onClose={() => setAnchor(null)}
        slotProps={{ paper: { sx: { bgcolor: "text.primary", color: "background.paper", minWidth: 200 } } }}>
        {FONT_SIZES.map((item) => (
          <MenuItem key={item.key} selected={item.size === current} sx={{ gap: 1.5, justifyContent: "space-between" }}
            onClick={() => { setAnchor(null); onChange(item.size); }}>
            <Box component="span" sx={{ fontWeight: 600, fontSize: `${Math.min(item.size, 32) / 16}rem` }}>{names[item.key]}</Box>
            <Typography variant="body2" component="span" sx={{ opacity: 0.7 }}>{item.size}</Typography>
          </MenuItem>
        ))}
      </Menu>
    </>
  );
}

interface PresetSelectProps {
  label: string;
  value: unknown;
  presets: readonly number[];
  onChange: (value: number) => void;
}

/** Choose one value from a short list. The current value shows even when it is not in the list. */
export function PresetSelect({ label, value, presets, onChange }: PresetSelectProps): React.JSX.Element {
  const current = typeof value === "number" ? Math.round(value * 10) / 10 : presets[0] ?? 0;
  const values = presets.includes(current) ? presets : [...presets, current].sort((a, b) => a - b);
  return (
    <ChoiceSelect
      label={label}
      value={String(current)}
      options={values.map((size) => ({ value: String(size), text: String(size) }))}
      onChange={(next) => onChange(Number(next))}
    />
  );
}
