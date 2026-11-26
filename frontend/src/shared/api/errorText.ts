import { ApiError, NETWORK_ERROR_CODE } from "@/shared/api/errors";
import { SHARED_TEXTS } from "@/shared/texts";

/** Return the text to show for an error. Never show `message` to the user. */
export function errorText(error: unknown): string {
  if (!(error instanceof ApiError)) return SHARED_TEXTS.error.unknown;
  if (error.code === NETWORK_ERROR_CODE) return SHARED_TEXTS.error.network;
  return SHARED_TEXTS.error.byCode[error.code] ?? SHARED_TEXTS.error.unknown;
}
