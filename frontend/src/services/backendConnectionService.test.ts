import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { BackendConnectionService } from "@/services/backendConnectionService";

describe("BackendConnectionService", () => {
  let service: BackendConnectionService;

  beforeEach(() => {
    service = new BackendConnectionService();
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    service.resetForTests();
    vi.unstubAllGlobals();
  });

  it("starts online without performing health checks", () => {
    expect(service.getSnapshot()).toEqual({ isOffline: false, isRetrying: false });
    expect(fetch).not.toHaveBeenCalled();
  });

  it("shows offline state when a real API request fails", async () => {
    const retry = vi.fn().mockRejectedValue(new TypeError("Failed to fetch"));
    service.reportOffline(retry);

    expect(service.getSnapshot().isOffline).toBe(true);
    expect(fetch).not.toHaveBeenCalled();
  });

  it("does not duplicate offline state on repeated failures", () => {
    const listener = vi.fn();
    service.subscribe(listener);

    service.reportOffline(vi.fn());
    expect(listener).toHaveBeenCalledTimes(2);

    listener.mockClear();
    service.reportOffline(vi.fn());

    expect(listener).not.toHaveBeenCalled();
    expect(service.getSnapshot().isOffline).toBe(true);
  });

  it("retries only when the user requests it", async () => {
    const retry = vi
      .fn()
      .mockRejectedValueOnce(new TypeError("Failed to fetch"))
      .mockResolvedValueOnce({ ok: true });

    service.reportOffline(retry);
    await service.retryLastRequest();

    expect(retry).toHaveBeenCalledTimes(1);
    expect(service.getSnapshot().isOffline).toBe(true);

    await service.retryLastRequest();
    expect(retry).toHaveBeenCalledTimes(2);
    expect(service.getSnapshot()).toEqual({ isOffline: false, isRetrying: false });
  });

  it("clears offline state after a successful API response", () => {
    service.reportOffline(vi.fn());
    service.notifyRequestSuccess();

    expect(service.getSnapshot()).toEqual({ isOffline: false, isRetrying: false });
  });
});
