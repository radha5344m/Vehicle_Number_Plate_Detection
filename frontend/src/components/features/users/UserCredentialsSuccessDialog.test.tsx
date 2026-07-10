import { UserCredentialsSuccessDialog } from "@/components/features/users/UserCredentialsSuccessDialog";
import { userFromUserItem } from "@/lib/userCredentials";
import type { UserItem } from "@/types/api/users";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

const sampleUser: UserItem = {
  officer_id: "off-1",
  user_id: "AP-26-03",
  employee_id: "STA001",
  full_name: "Priya Rao",
  username: "priya01",
  email: "priya01@sentinelanpr.ai",
  phone_number: null,
  badge_number: "AP001",
  rank: "Inspector",
  role: "STATION_ADMIN",
  police_station: "Ongole Town",
  district: "Prakasam",
  status: "active",
  created_at: "2026-07-09T00:00:00.000Z",
  last_login_at: null,
};

describe("UserCredentialsSuccessDialog", () => {
  it("renders create credentials with hidden password by default", () => {
    render(
      <UserCredentialsSuccessDialog
        user={userFromUserItem(sampleUser)}
        temporaryPassword="STA001@2026"
        mode="create"
        onClose={vi.fn()}
      />,
    );

    expect(screen.getByText("User Created Successfully")).toBeInTheDocument();
    expect(screen.getByText("Login Credentials")).toBeInTheDocument();
    expect(screen.getByText("AP-26-03")).toBeInTheDocument();
    expect(screen.getByText("priya01")).toBeInTheDocument();
    expect(screen.getByText("STA001")).toBeInTheDocument();
    expect(screen.getByText("AP001")).toBeInTheDocument();
    expect(screen.queryByText("STA001@2026")).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Copy All Credentials" })).toBeInTheDocument();
  });
});
