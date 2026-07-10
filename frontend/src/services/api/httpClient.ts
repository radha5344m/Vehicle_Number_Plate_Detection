import { clearAuth, getAccessToken } from "@/stores/authStore";
import { env } from "@/config/env";
import { monitoredFetch } from "@/services/api/monitoredFetch";
import type { ApiResponse } from "@/types/api/common";
import type { ApiErrorEnvelope } from "@/types/api/auth";

export class HttpError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly code?: string,
  ) {
    super(message);
    this.name = "HttpError";
  }
}

const LOGIN_PATH = "/login";

const PUBLIC_API_PATHS = new Set(["/v1/health", "/v1/auth/login"]);

function normalizeApiPath(path: string): string {
  return path.split("?")[0] ?? path;
}

function requiresAuthentication(path: string): boolean {
  const normalized = normalizeApiPath(path);
  return normalized.startsWith("/v1/") && !PUBLIC_API_PATHS.has(normalized);
}

function resolveAccessToken(): string | null {
  const token = getAccessToken()?.trim();
  return token ? token : null;
}

/**
 * Handle an expired/invalid session. The backend has no token-refresh
 * endpoint, so a 401 on an authenticated request means the officer must
 * sign in again. Clear the stale session and redirect to login (preserving
 * the current path) instead of leaving the page stuck on failed requests.
 */
function handleUnauthorized(): void {
  clearAuth();
  if (typeof window === "undefined") return;
  if (window.location.pathname.startsWith(LOGIN_PATH)) return;
  const current = `${window.location.pathname}${window.location.search}`;
  const redirect = encodeURIComponent(current);
  window.location.assign(`${LOGIN_PATH}?reason=session_expired&redirect=${redirect}`);
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const base = env.apiBaseUrl.replace(/\/$/, "");
  const url = `${base}${path.startsWith("/") ? path : `/${path}`}`;
  const token = resolveAccessToken();

  if (requiresAuthentication(path) && !token) {
    throw new HttpError(
      "Authentication is required. Please sign in and try again.",
      401,
      "AUTH_MISSING",
    );
  }

  const headers: Record<string, string> = {
    Accept: "application/json",
    ...(init?.headers as Record<string, string> | undefined),
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  if (init?.body && !headers["Content-Type"] && !(init.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  let response: Response;
  try {
    response = await monitoredFetch(url, {
      ...init,
      headers,
    });
  } catch {
    throw new HttpError("Unable to reach the backend service.", 0, "NETWORK_ERROR");
  }

  if (!response.ok) {
    let message = `HTTP ${response.status}`;
    let code: string | undefined;
    try {
      const body = (await response.json()) as ApiErrorEnvelope;
      if (body.error) {
        code = body.error.code;
        const detailMessages = (body.error.details ?? [])
          .map((item) => item.message)
          .filter(Boolean);
        message =
          detailMessages.length > 0
            ? detailMessages.join(" ")
            : body.error.message || message;
      }
    } catch {
      // ignore parse errors
    }
    if (response.status === 404 && path.startsWith("/v1/")) {
      message =
        "API route not found. If the frontend and backend are on different hosts, " +
        "set VITE_API_BASE_URL to your backend URL when building the frontend.";
    }
    // A 401 on any request other than the login attempt itself means the
    // session has expired; recover by signing the officer out.
    if (response.status === 401 && !url.includes("/auth/login")) {
      handleUnauthorized();
    }
    throw new HttpError(message, response.status, code);
  }

  return response.json() as Promise<T>;
}

export async function getJson<T>(path: string, init?: RequestInit): Promise<T> {
  return request<T>(path, {
    ...init,
    method: init?.method ?? "GET",
  });
}

export async function postJson<T>(path: string, body: unknown): Promise<T> {
  return request<T>(path, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function patchJson<T>(path: string, body: unknown): Promise<T> {
  return request<T>(path, {
    method: "PATCH",
    body: JSON.stringify(body),
  });
}

export async function putJson<T>(path: string, body: unknown): Promise<T> {
    return request<T>(path, {
        method: "PUT",
        body: JSON.stringify(body),
    });
}

export async function deleteJson<T>(path: string): Promise<T> {
  return request<T>(path, {
    method: "DELETE",
  });
}

export async function getApiData<T>(path: string, init?: RequestInit): Promise<T> {
  const envelope = await getJson<ApiResponse<T>>(path, init);
  return envelope.data;
}

/** GET helper for protected endpoints — always requires a stored access token. */
export async function getAuthenticatedApiData<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  if (!resolveAccessToken()) {
    throw new HttpError(
      "Authentication is required. Please sign in and try again.",
      401,
      "AUTH_MISSING",
    );
  }
  return getApiData<T>(path, init);
}

export async function postApiData<T>(path: string, body: unknown): Promise<T> {
  const envelope = await postJson<ApiResponse<T>>(path, body);
  return envelope.data;
}

export async function patchApiData<T>(path: string, body: unknown): Promise<T> {
  const envelope = await patchJson<ApiResponse<T>>(path, body);
  return envelope.data;
}

export async function putApiData<T>(path: string, body: unknown): Promise<T> {
  const envelope = await putJson<ApiResponse<T>>(path, body);
  return envelope.data;
}

export async function deleteApiData<T>(path: string): Promise<T> {
  const envelope = await deleteJson<ApiResponse<T>>(path);
  return envelope.data;
}

export async function postFormDataApi<T>(
  path: string,
  formData: FormData,
  extraHeaders?: Record<string, string>,
): Promise<T> {
  const envelope = await request<ApiResponse<T>>(path, {
    method: "POST",
    body: formData,
    headers: extraHeaders,
  });
  return envelope.data;
}
