import { authStorage } from "../lib/storage";
import type { ApiEnvelope, ApiErrorPayload } from "./types";

const API_BASE_URL = (import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1").replace(/\/$/, "");

export class ApiError extends Error {
  readonly code: string;
  readonly status: number;

  constructor(code: string, message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.code = code;
    this.status = status;
  }
}

interface RequestOptions extends Omit<RequestInit, "body"> {
  body?: unknown;
}

async function parseJson(response: Response): Promise<unknown> {
  const contentType = response.headers.get("content-type") ?? "";
  return contentType.includes("application/json") ? response.json() : null;
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<ApiEnvelope<T>> {
  const token = authStorage.getToken();
  const headers = new Headers(options.headers);
  headers.set("Accept", "application/json");
  if (options.body !== undefined && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
    body: options.body instanceof FormData ? options.body : options.body === undefined ? undefined : JSON.stringify(options.body),
  });
  const payload = await parseJson(response);
  if (!response.ok) {
    const error = payload as Partial<ApiErrorPayload> | null;
    throw new ApiError(
      error?.error?.code ?? "request_failed",
      error?.error?.message ?? "Something went wrong. Please try again.",
      response.status,
    );
  }
  if (!payload || typeof payload !== "object" || !("data" in payload)) {
    throw new ApiError("invalid_response", "The server returned an unexpected response.", response.status);
  }
  return payload as ApiEnvelope<T>;
}

export const api = {
  async get<T>(path: string): Promise<T> {
    return (await request<T>(path, { method: "GET" })).data;
  },
  async getWithMeta<T>(path: string): Promise<ApiEnvelope<T>> {
    return request<T>(path, { method: "GET" });
  },
  post<T>(path: string, body?: unknown): Promise<T> {
    return request<T>(path, { method: "POST", body }).then((envelope) => envelope.data);
  },
  upload<T>(path: string, formData: FormData): Promise<T> {
    return request<T>(path, { method: "POST", body: formData }).then((envelope) => envelope.data);
  },  async delete<T>(path: string): Promise<T> {
    return request<T>(path, { method: "DELETE" }).then((envelope) => envelope.data);
  },};
