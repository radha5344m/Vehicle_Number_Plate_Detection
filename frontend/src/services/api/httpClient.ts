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
  const token = getAccessToken();
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
    // A 401 on any request other than the login attempt itself means the
    // session has expired; recover by signing the officer out.
    if (response.status === 401 && !url.includes("/auth/login")) {
      handleUnauthorized();
    }
    throw new HttpError(message, response.status, code);
  }

  return response.json() as Promise<T>;
}

export async function getJson<T>(path: string): Promise<T> {
  return request<T>(path);
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

export async function getApiData<T>(path: string): Promise<T> {
  const envelope = await getJson<ApiResponse<T>>(path);
  return envelope.data;
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

export async function postFormDataApi<T>(path: string, formData: FormData): Promise<T> {
  const envelope = await request<ApiResponse<T>>(path, {
    method: "POST",
    body: formData,
  });
  return envelope.data;
}
