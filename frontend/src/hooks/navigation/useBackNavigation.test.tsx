import { describe, expect, it, beforeEach } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import type { ReactNode } from "react";

import { useBackNavigation } from "@/hooks/navigation/useBackNavigation";
import { setAuth } from "@/stores/authStore";

function wrapper({ children }: { children: ReactNode }) {
  return <MemoryRouter>{children}</MemoryRouter>;
}

describe("useBackNavigation", () => {
  beforeEach(() => {
    sessionStorage.clear();
    Object.defineProperty(window.history, "state", {
      configurable: true,
      value: { idx: 0 },
    });
  });

  it("returns a callable back navigation handler", () => {
    setAuth(
      "token",
      "refresh",
      {
        officer_id: "off-1",
        employee_id: "EMP-1",
        badge_number: "badge",
        username: "admin001",
        email: "a@test.com",
        phone_number: null,
        first_name: "Admin",
        last_name: "User",
        rank: "Director",
        station_id: "hq",
        station_code: "HQ",
        station_name: "HQ",
        district: "Test",
        roles: ["super_admin"],
      },
      "SUPER_ADMIN",
      ["dashboard"],
      { station_id: "hq", station_code: "HQ", station_name: "HQ" },
    );

    const { result } = renderHook(() => useBackNavigation(), { wrapper });
    expect(typeof result.current).toBe("function");

    act(() => {
      result.current();
    });
  });
});
