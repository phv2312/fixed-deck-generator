/** Pure edits of a table draft. A highlight index follows its row or column when others move. */
export interface TableDraft {
  rows: string[][];
  header: boolean;
  /** Counts the rows below the header, as the API does. */
  highlightRow: number | null;
  highlightCol: number | null;
  /** The note under the table. An empty text means no note. */
  caption: string;
}

const blank = (count: number): string[] => Array.from({ length: count }, () => "");

const num = (value: unknown): number | null => (typeof value === "number" ? value : null);

/** Read the draft of a table element from its props. */
export function toDraft(props: Record<string, unknown>): TableDraft {
  const rows = Array.isArray(props.rows) ? (props.rows as string[][]).map((row) => [...row]) : [];
  return { rows, header: props.header !== false, highlightRow: num(props.highlight_row), highlightCol: num(props.highlight_col), caption: typeof props.caption === "string" ? props.caption : "" };
}

/** The changes that save a draft. */
export function toChanges(draft: TableDraft): Record<string, unknown> {
  return {
    rows: draft.rows,
    highlight_row: draft.highlightRow,
    highlight_col: draft.highlightCol,
    caption: draft.caption.trim() === "" ? null : draft.caption,
  };
}

export const columnCount = (draft: TableDraft): number => draft.rows[0]?.length ?? 0;

/** The header row stays the first row, so it cannot be removed. */
export const canRemoveRow = (draft: TableDraft, at: number): boolean =>
  draft.rows.length > 1 && !(draft.header && at === 0);

export const canRemoveColumn = (draft: TableDraft): boolean => columnCount(draft) > 1;

/** Insert an empty row below row `at`. */
export function insertRowBelow(draft: TableDraft, at: number): TableDraft {
  const rows = [...draft.rows.slice(0, at + 1), blank(columnCount(draft)), ...draft.rows.slice(at + 1)];
  const body = at + 1 - (draft.header ? 1 : 0); // index of the new row among the body rows
  const hot = draft.highlightRow;
  return { ...draft, rows, highlightRow: hot !== null && body <= hot ? hot + 1 : hot };
}

export function removeRow(draft: TableDraft, at: number): TableDraft {
  if (!canRemoveRow(draft, at)) return draft;
  const body = at - (draft.header ? 1 : 0);
  const hot = draft.highlightRow;
  const next = hot === null || body > hot ? hot : body === hot ? null : hot - 1;
  return { ...draft, rows: draft.rows.filter((_, index) => index !== at), highlightRow: next };
}

/** Insert an empty column right of column `at`. */
export function insertColumnRight(draft: TableDraft, at: number): TableDraft {
  const rows = draft.rows.map((row) => [...row.slice(0, at + 1), "", ...row.slice(at + 1)]);
  const hot = draft.highlightCol;
  return { ...draft, rows, highlightCol: hot !== null && at + 1 <= hot ? hot + 1 : hot };
}

export function removeColumn(draft: TableDraft, at: number): TableDraft {
  if (!canRemoveColumn(draft)) return draft;
  const hot = draft.highlightCol;
  const next = hot === null || at > hot ? hot : at === hot ? null : hot - 1;
  return { ...draft, rows: draft.rows.map((row) => row.filter((_, index) => index !== at)), highlightCol: next };
}

export function setCell(draft: TableDraft, r: number, c: number, text: string): TableDraft {
  const rows = draft.rows.map((row, ri) => (ri === r ? row.map((cell, ci) => (ci === c ? text : cell)) : row));
  return { ...draft, rows };
}
