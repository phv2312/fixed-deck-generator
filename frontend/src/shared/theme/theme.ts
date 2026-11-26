/**
 * Token plan
 *
 * Subject: a workspace where an agent builds slide decks. Audience: people who make decks.
 * Primary job: start a deck, then review what the agent made.
 *
 * Color (4 to 6 named colors):
 *   teal     #0F5F66  primary action
 *   ink      #1F2430  text
 *   paper    #F6F7F9  page background, white surfaces on top
 *   line     #DDE1E8  borders and dividers
 *   amber    #7A4A00  warning: the agent waits for the user
 *   green    #16643B  success;  red #9B2C2C  error
 * Type: one system font stack, about five sizes, one scale.
 * Layout: a bar on top, a content column, cards in a grid. One strong button per screen.
 * Principles: quiet neutrals, one teal action, state shown by shape and text, not by color alone.
 *
 * This file is the only place for colors, fonts, spacing, radius and shadow.
 */
import { createTheme } from "@mui/material/styles";

const INK = "#1F2430";
const INK_SOFT = "#5A6272";
const PAPER = "#F6F7F9";
const SURFACE = "#FFFFFF";
const LINE = "#DDE1E8";
const TEAL = "#0F5F66";

export const theme = createTheme({
  spacing: 8,
  shape: { borderRadius: 8 },
  palette: {
    mode: "light",
    primary: { main: TEAL, contrastText: SURFACE },
    success: { main: "#16643B" },
    warning: { main: "#7A4A00" },
    error: { main: "#9B2C2C" },
    info: { main: "#1B4F8F" },
    text: { primary: INK, secondary: INK_SOFT },
    background: { default: PAPER, paper: SURFACE },
    divider: LINE,
  },
  typography: {
    fontFamily: 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif',
    fontSize: 16,
    h1: { fontSize: "1.75rem", fontWeight: 700, lineHeight: 1.3 },
    h2: { fontSize: "1.5rem", fontWeight: 700, lineHeight: 1.3 },
    h3: { fontSize: "1.125rem", fontWeight: 700, lineHeight: 1.4 },
    body1: { fontSize: "1rem", lineHeight: 1.5 },
    body2: { fontSize: "0.875rem", lineHeight: 1.5 },
    caption: { fontSize: "0.75rem", lineHeight: 1.5 },
    button: { textTransform: "none", fontWeight: 600 },
  },
  components: {
    MuiButton: {
      defaultProps: { disableElevation: true },
      styleOverrides: { root: { minHeight: 44 } },
    },
    MuiIconButton: { styleOverrides: { root: { minWidth: 44, minHeight: 44 } } },
    MuiCardActionArea: {
      styleOverrides: {
        root: ({ theme: t }) => ({
          "&.Mui-focusVisible": { outline: `2px solid ${t.palette.primary.main}`, outlineOffset: -2 },
        }),
      },
    },
    MuiCard: {
      defaultProps: { variant: "outlined" },
      styleOverrides: { root: { boxShadow: "none" } },
    },
    MuiDialog: {
      styleOverrides: { paper: { boxShadow: "0 4px 12px rgba(31, 36, 48, 0.18)" } },
    },
  },
});
