import { ApiError, NETWORK_ERROR_CODE, UNKNOWN_ERROR_CODE, type ErrorDetail } from "@/shared/api/errors";

const BASE_URL: string = import.meta.env.VITE_API_BASE_URL ?? "";

export interface RequestOptions {
  method?: "GET" | "POST" | "PATCH" | "PUT" | "DELETE";
  query?: Record<string, string | number | undefined>;
  body?: unknown;
  signal?: AbortSignal;
}

interface ErrorBody {
  code: string;
  message: string;
  details: ErrorDetail[] | null;
}

function isErrorBody(value: unknown): value is ErrorBody {
  if (typeof value !== "object" || value === null) return false;
  return "code" in value && typeof value.code === "string" && "message" in value;
}

function buildUrl(path: string, query: RequestOptions["query"]): string {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(query ?? {})) {
    if (value !== undefined) params.set(key, String(value));
  }
  const suffix = params.size > 0 ? `?${params.toString()}` : "";
  return `${BASE_URL}${path}${suffix}`;
}

async function toError(response: Response): Promise<ApiError> {
  const body: unknown = await response.json().catch(() => null);
  if (isErrorBody(body)) {
    return new ApiError(body.code, String(body.message), response.status, body.details ?? null);
  }
  return new ApiError(UNKNOWN_ERROR_CODE, response.statusText, response.status, null);
}

async function send(path: string, options: RequestOptions): Promise<Response> {
  const headers: Record<string, string> = { "X-Request-ID": crypto.randomUUID() };
  if (options.body !== undefined) headers["Content-Type"] = "application/json";
  let response: Response;
  try {
    response = await fetch(buildUrl(path, options.query), {
      method: options.method ?? "GET",
      headers,
      body: options.body === undefined ? undefined : JSON.stringify(options.body),
      signal: options.signal,
    });
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") throw error;
    throw new ApiError(NETWORK_ERROR_CODE, "network error", 0, null);
  }
  if (!response.ok) throw await toError(response);
  return response;
}

/** Make one call to the API. Turn every failure into an `ApiError`. */
export async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const response = await send(path, options);
  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

/** Make one call to the API and return the body as text. */
export async function apiText(path: string, options: RequestOptions = {}): Promise<string> {
  return (await send(path, options)).text();
}

/** Return the URL of an API path, for a link or an image that the browser loads itself. */
export function apiUrl(path: string, query?: RequestOptions["query"]): string {
  return buildUrl(path, query);
}

/** Turn a failed response into an `ApiError`. */
export const responseError = toError;
