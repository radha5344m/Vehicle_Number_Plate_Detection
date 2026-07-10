import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it } from "vitest";
import { MemoryRouter, Route, Routes } from "react-router-dom";

import { PATHS } from "@/routes/paths";
import { PermissionGuard } from "@/routes/guards/PermissionGuard";
import { setAuth } from "@/stores/authStore";

function renderGuard(requiredPermissions: string[]) {
  return render(
    <MemoryRouter initialEntries={["/protected"]}>
      <Routes>
        <Route
          path="/protected"
          element={
            <PermissionGuard requiredPermissions={requiredPermissions}>
              <div>Protected Content</div>
            </PermissionGuard>
          }
        />
        <Route path={PATHS.ACCESS_DENIED} element={<div>Access Denied Page</div>} />
        <Route path={PATHS.LOGIN} element={<div>Login Page</div>} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("PermissionGuard", () => {
  beforeEach(() => {
    sessionStorage.clear();
  });

  it("redirects unauthenticated users to login", () => {
    renderGuard(["dashboard"]);
    expect(screen.getByText("Login Page")).toBeInTheDocument();
  });

  it("redirects authenticated users without permission to the 403 page", () => {
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
      ["dashboard"],
      {
        station_id: "station-1",
        station_code: "ONG01",
        station_name: "Ongole Town",
      },
    );

    renderGuard(["analytics"]);
    expect(screen.getByText("Access Denied Page")).toBeInTheDocument();
  });

  it("renders children when the permission is present", () => {
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
      ["dashboard", "reports"],
      {
        station_id: "station-1",
        station_code: "ONG01",
        station_name: "Ongole Town",
      },
    );

    renderGuard(["reports"]);
    expect(screen.getByText("Protected Content")).toBeInTheDocument();
  });
});
