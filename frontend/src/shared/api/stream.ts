import { fetchEventSource } from "@microsoft/fetch-event-source";

import { responseError } from "@/shared/api/client";
import { ApiError, NETWORK_ERROR_CODE } from "@/shared/api/errors";

const BASE_URL: string = import.meta.env.VITE_API_BASE_URL ?? "";

export interface StreamOptions<E> {
  body: unknown;
  signal?: AbortSignal;
  /** Called for each server-sent event. `type` is the SSE event name, `data` the parsed JSON. */
  onEvent: (event: E) => void;
}

/** POST a JSON body and read the server-sent events of the answer. Fail with an `ApiError`. */
export async function streamRequest<E>(path: string, options: StreamOptions<E>): Promise<void> {
  try {
    await fetchEventSource(`${BASE_URL}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Request-ID": crypto.randomUUID() },
      body: JSON.stringify(options.body),
      signal: options.signal,
      openWhenHidden: true,
      async onopen(response) {
        if (!response.ok) throw await responseError(response);
      },
      onmessage(message) {
        if (message.data) options.onEvent(JSON.parse(message.data) as E);
      },
      onerror(error: unknown) {
        throw error;
      },
    });
  } catch (error) {
    if (error instanceof ApiError) throw error;
    if (error instanceof DOMException && error.name === "AbortError") throw error;
    throw new ApiError(NETWORK_ERROR_CODE, "network error", 0, null);
  }
}
