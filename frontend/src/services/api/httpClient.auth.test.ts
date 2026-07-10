import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

const monitoredFetchMock = vi.fn();

vi.mock("@/services/api/monitoredFetch", () => ({
  monitoredFetch: monitoredFetchMock,
}));

vi.mock("@/config/env", () => ({
  env: {
    apiBaseUrl: "http://localhost:8080",
    appEnv: "test",
    isProduction: false,
  },
}));

describe("httpClient authenticated requests", () => {
  beforeEach(() => {
    monitoredFetchMock.mockReset();
    sessionStorage.clear();
  });

  afterEach(() => {
    sessionStorage.clear();
  });

  it("attaches Authorization Bearer token to vision progress polling", async () => {
    sessionStorage.setItem("sentinel_access_token", "test-jwt-token");

    monitoredFetchMock.mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        data: {
          message: "Vision AI busy...",
          attempt: 0,
          max_attempts: 5,
          phase: "busy",
        },
        meta: { correlation_id: "corr-123" },
      }),
    });

    const { getAuthenticatedApiData } = await import("@/services/api/httpClient");
    await getAuthenticatedApiData(
      "/v1/workflow/vision-progress?correlation_id=corr-123",
    );

    expect(monitoredFetchMock).toHaveBeenCalledTimes(1);
    const [, init] = monitoredFetchMock.mock.calls[0] as [string, RequestInit];
    expect(init.method).toBe("GET");
    expect(init.headers).toMatchObject({
      Authorization: "Bearer test-jwt-token",
      Accept: "application/json",
    });
  });

  it("does not call the API when no access token is stored", async () => {
    const { getAuthenticatedApiData } = await import("@/services/api/httpClient");

    await expect(
      getAuthenticatedApiData("/v1/workflow/vision-progress?correlation_id=corr-123"),
    ).rejects.toMatchObject({ code: "AUTH_MISSING" });

    expect(monitoredFetchMock).not.toHaveBeenCalled();
  });
});
