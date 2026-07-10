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

  it("attaches Authorization Bearer token to workflow verification requests", async () => {
    sessionStorage.setItem("sentinel_access_token", "test-jwt-token");

    monitoredFetchMock.mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        data: {
          status: "completed",
          workflow_id: "wf-1",
          registration_number: "AP09AB1234",
          completed_at: "2026-07-10T00:00:00Z",
        },
        meta: { correlation_id: "corr-123" },
      }),
    });

    const { postFormDataApi } = await import("@/services/api/httpClient");
    const formData = new FormData();
    formData.append("vehicle_image", new File(["x"], "vehicle.jpg", { type: "image/jpeg" }));
    await postFormDataApi("/v1/workflow/vehicle-verification", formData);

    expect(monitoredFetchMock).toHaveBeenCalledTimes(1);
    const [, init] = monitoredFetchMock.mock.calls[0] as [string, RequestInit];
    expect(init.method).toBe("POST");
    expect(init.headers).toMatchObject({
      Authorization: "Bearer test-jwt-token",
      Accept: "application/json",
    });
  });

  it("does not call the API when no access token is stored", async () => {
    const { getAuthenticatedApiData } = await import("@/services/api/httpClient");

    await expect(
      getAuthenticatedApiData("/v1/workflow/vehicle-verification"),
    ).rejects.toMatchObject({ code: "AUTH_MISSING" });

    expect(monitoredFetchMock).not.toHaveBeenCalled();
  });
});
