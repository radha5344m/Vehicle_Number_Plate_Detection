import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { DashboardPage } from "@/pages/dashboard/DashboardPage";
import { setAuth } from "@/stores/authStore";

vi.mock("@/hooks/dashboard/useExecutiveDashboard", () => ({
  useExecutiveDashboard: () => ({
    data: {
      scope_label: "System Wide",
      kpis: [
        { label: "Total Investigations", value: 12, display_value: "12" },
        { label: "Verified Vehicles", value: 10, display_value: "10" },
      ],
      daily_trend: [{ label: "2026-07-08", value: 12 }],
      weekly_trend: [{ label: "2026-W28", value: 12 }],
      monthly_trend: [{ label: "2026-07", value: 12 }],
      hourly_activity: [{ label: "09:00", value: 3 }],
      investigation_status_distribution: [{ label: "completed", value: 12 }],
      risk_distribution: [{ label: "high", value: 2 }],
      risk_trend: [{ label: "2026-07-08", value: 2 }],
      top_high_risk_registrations: [{ label: "AP09AA1234", value: 2 }],
      frequent_suspicious_vehicles: [{ label: "AP09AA1234", value: 2 }],
      vehicle_type_distribution: [{ label: "SUV", value: 4 }],
      vehicle_brand_distribution: [{ label: "Mahindra", value: 3 }],
      vehicle_color_distribution: [{ label: "White", value: 5 }],
      registration_state_distribution: [{ label: "AP", value: 10 }],
      common_vehicle_models: [{ label: "Scorpio", value: 2 }],
      top_performing_officers: [{ name: "Officer Ravi", metric: "Verified Vehicles", value: 6 }],
      most_active_officers: [{ name: "Officer Ravi", metric: "Investigations Completed", value: 8 }],
      officer_leaderboard: [{ name: "Officer Ravi", metric: "High Risk Detections", value: 2 }],
      top_performing_stations: [{ name: "Ongole Town", metric: "Verification Volume", value: 9 }],
      recent_investigations: [],
      recent_high_risk_alerts: [],
      recent_officer_activity: [],
      recent_reports_generated: [],
      ai_metrics: [{ label: "Average AI Confidence", value: 96, display_value: "96.0%" }],
      insights: [{ title: "Top detected brand", detail: "Most detected vehicle brand: Mahindra." }],
      connection_status: {
        status: "Connected",
        last_updated_at: "2026-07-08T10:00:00Z",
        auto_refresh_seconds: 45,
      },
    },
    loading: false,
    error: null,
    filters: {},
    setFilters: vi.fn(),
    refresh: vi.fn(),
    exportDashboard: vi.fn(),
  }),
}));

describe("DashboardPage", () => {
  beforeEach(() => {
    sessionStorage.clear();
    setAuth(
      "access-token",
      "refresh-token",
      {
        officer_id: "super-admin-id",
        employee_id: "EMP-ADMIN",
        badge_number: "superadmin",
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
      ["dashboard", "analytics", "reports", "profile"],
      {
        station_id: "hq",
        station_code: "HQ",
        station_name: "Headquarters",
      },
    );
  });

  it("renders the executive command center", () => {
    render(
      <MemoryRouter>
        <DashboardPage />
      </MemoryRouter>,
    );

    expect(screen.getByText("Executive Command Center")).toBeInTheDocument();
    expect(screen.getByText("Total Investigations")).toBeInTheDocument();
    expect(screen.queryByText("Executive Filters")).not.toBeInTheDocument();
    expect(screen.getByText("Top Performing Officers")).toBeInTheDocument();
    expect(screen.getByText("Executive Insights")).toBeInTheDocument();
    expect(screen.getByText(/auto refresh 45s/i)).toBeInTheDocument();
  });
});
