import { cleanup, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { AppLayout } from "@/layouts/AppLayout";
import { setAuth } from "@/stores/authStore";

vi.mock("@/hooks/auth/useAuth", () => ({
  useAuth: () => ({
    logout: vi.fn(),
  }),
}));

describe("AppLayout", () => {
  beforeEach(() => {
    sessionStorage.clear();
  });

  afterEach(() => {
    cleanup();
  });

  it("renders the police officer sidebar without admin-only entries", () => {
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
      ["dashboard", "vehicle_verification", "investigation_history", "reports", "profile"],
      {
        station_id: "station-1",
        station_code: "ONG01",
        station_name: "Ongole Town",
      },
    );

    render(
      <MemoryRouter>
        <AppLayout>
          <div>Officer Content</div>
        </AppLayout>
      </MemoryRouter>,
    );

    expect(screen.getByText("Dashboard")).toBeInTheDocument();
    expect(screen.getByText("Vehicle Verification")).toBeInTheDocument();
    expect(screen.getByText("My Investigations")).toBeInTheDocument();
    expect(screen.getByText("My Reports")).toBeInTheDocument();
    expect(screen.getByText("Notifications")).toBeInTheDocument();
    expect(screen.getByText("Profile")).toBeInTheDocument();

    expect(screen.queryByText("Users")).not.toBeInTheDocument();
    expect(screen.queryByText("Police Stations")).not.toBeInTheDocument();
    expect(screen.queryByText("Management")).not.toBeInTheDocument();
    expect(screen.queryByText("Analytics")).not.toBeInTheDocument();
    expect(screen.queryByText("Settings")).not.toBeInTheDocument();
  });

  it("renders the management sidebar entry for super admin", () => {
    setAuth(
      "access-token",
      "refresh-token",
      {
        officer_id: "super-admin",
        employee_id: "EMP-ADMIN",
        badge_number: "SUPERADMIN",
        username: "superadmin",
        email: "admin@sentinelanpr.ai",
        phone_number: null,
        first_name: "System",
        last_name: "Administrator",
        rank: "Director",
        station_id: "hq",
        station_code: "HQ",
        station_name: "Headquarters",
        district: "Prakasam",
        roles: ["super_admin"],
      },
      "SUPER_ADMIN",
      ["dashboard", "vehicle_verification", "investigation_history", "reports", "analytics", "users", "stations", "notifications", "profile"],
      {
        station_id: "hq",
        station_code: "HQ",
        station_name: "Headquarters",
      },
    );

    render(
      <MemoryRouter>
        <AppLayout>
          <div>Admin Content</div>
        </AppLayout>
      </MemoryRouter>,
    );

    expect(screen.getByText("Management")).toBeInTheDocument();
    expect(screen.getByText("Notifications")).toBeInTheDocument();
    expect(screen.queryByText("Users")).not.toBeInTheDocument();
    expect(screen.queryByText("Police Stations")).not.toBeInTheDocument();
  });

  it("renders the management sidebar entry for station admin", () => {
    setAuth(
      "access-token",
      "refresh-token",
      {
        officer_id: "station-admin",
        employee_id: "EMP-ST",
        badge_number: "STADMIN",
        username: "stadmin",
        email: "stadmin@example.com",
        phone_number: null,
        first_name: "Station",
        last_name: "Admin",
        rank: "Inspector",
        station_id: "station-1",
        station_code: "ONG01",
        station_name: "Ongole Town",
        district: "Prakasam",
        roles: ["station_admin"],
      },
      "STATION_ADMIN",
      [
        "dashboard",
        "vehicle_verification",
        "investigation_history",
        "reports",
        "analytics",
        "officers",
        "notifications",
        "profile",
      ],
      {
        station_id: "station-1",
        station_code: "ONG01",
        station_name: "Ongole Town",
      },
    );

    render(
      <MemoryRouter>
        <AppLayout>
          <div>Station Admin Content</div>
        </AppLayout>
      </MemoryRouter>,
    );

    expect(screen.getByText("Management")).toBeInTheDocument();
    expect(screen.queryByText("Users")).not.toBeInTheDocument();
    expect(screen.queryByText("Police Stations")).not.toBeInTheDocument();
  });
});
