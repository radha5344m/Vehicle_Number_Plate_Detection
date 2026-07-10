import { describe, expect, it } from "vitest";

import {
  buildCredentialsText,
  formatRoleLabel,
  showBadgeNumber,
} from "@/lib/userCredentials";

describe("userCredentials", () => {
  const baseUser = {
    officer_id: "off-1",
    username: "priya01",
    employee_id: "EMP-001",
    badge_number: "AP001",
    role: "POLICE_OFFICER",
    full_name: "Priya Rao",
    police_station: "Ongole Town",
  };

  it("formats role labels", () => {
    expect(formatRoleLabel("STATION_ADMIN")).toBe("STATION ADMIN");
  });

  it("hides badge number for super admin", () => {
    expect(showBadgeNumber("SUPER_ADMIN")).toBe(false);
    expect(showBadgeNumber("POLICE_OFFICER")).toBe(true);
  });

  it("builds credential text with password", () => {
    const text = buildCredentialsText(baseUser, "Temp@12345");
    expect(text).toContain("Username: priya01");
    expect(text).toContain("Employee ID: EMP-001");
    expect(text).toContain("Badge Number: AP001");
    expect(text).toContain("Temporary Password: Temp@12345");
  });

  it("omits badge number for super admin", () => {
    const text = buildCredentialsText(
      { ...baseUser, role: "SUPER_ADMIN", badge_number: "SUPERADMIN" },
      "Admin@123456",
    );
    expect(text).not.toContain("Badge Number:");
  });
});
