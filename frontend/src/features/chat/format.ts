import type { ToolCall } from "@/features/chat/types";

const KB = 1024;
const MB = KB * KB;

export function formatBytes(size: number): string {
  if (size >= MB) return `${(size / MB).toFixed(1)} MB`;
  if (size >= KB) return `${(size / KB).toFixed(1)} KB`;
  return `${size} B`;
}

export function countTools(calls: ToolCall[]): { running: number; failed: number } {
  return {
    running: calls.filter((call) => call.status === "running").length,
    failed: calls.filter((call) => call.status === "error").length,
  };
}

export function isImage(mime: string): boolean {
  return mime.startsWith("image/");
}
