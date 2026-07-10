import { beforeEach, describe, expect, it } from "vitest";

import { getAuthSession, setAuth } from "@/stores/authStore";
import { hasAnyRole, hasPermission, hasRole } from "@/lib/rbac";

describe("rbac helpers", () => {
  beforeEach(() => {
    sessionStorage.clear();
  });

  it("reads permissions and roles from the stored auth session", () => {
    setAuth(
      "access-token",
      "refresh-token",
      {
        officer_id: "officer-1",
        employee_id: "EMP-1",
        badge_number: "AP001",
        username: "ap001",
        email: "ap001@example.com",
        phone_number: null,
        first_name: "Ravi",
        last_name: "Kumar",
        rank: "Inspector",
        station_id: "station-1",
        station_code: "ONG01",
        station_name: "Ongole Town",
        district: "Prakasam",
        roles: ["police_officer"],
      },
      "POLICE_OFFICER",
      ["dashboard", "reports", "profile"],
      {
        station_id: "station-1",
        station_code: "ONG01",
        station_name: "Ongole Town",
      },
    );

    expect(getAuthSession()?.role).toBe("POLICE_OFFICER");
    expect(hasRole("POLICE_OFFICER")).toBe(true);
    expect(hasAnyRole(["SUPER_ADMIN", "POLICE_OFFICER"])).toBe(true);
    expect(hasPermission("reports")).toBe(true);
    expect(hasPermission("users")).toBe(false);
  });
});
