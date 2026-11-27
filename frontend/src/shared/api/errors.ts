export interface ErrorDetail {
  loc: (string | number)[];
  msg: string;
}

/** The one error type of the API client. Code branches on `code`, never on `message`. */
export class ApiError extends Error {
  readonly code: string;
  readonly status: number;
  readonly details: ErrorDetail[] | null;

  constructor(code: string, message: string, status: number, details: ErrorDetail[] | null) {
    super(message);
    this.name = "ApiError";
    this.code = code;
    this.status = status;
    this.details = details;
  }
}

export const NETWORK_ERROR_CODE = "NetworkError";
export const UNKNOWN_ERROR_CODE = "UnknownError";
