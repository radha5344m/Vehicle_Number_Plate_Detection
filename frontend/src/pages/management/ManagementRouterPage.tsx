import { hasRole } from "@/lib/rbac";
import { PoliceOfficersPage } from "@/pages/stationAdmin/PoliceOfficersPage";
import { ManagementPage } from "@/pages/management/ManagementPage";

export function ManagementRouterPage() {
  if (hasRole("STATION_ADMIN")) {
    return <PoliceOfficersPage />;
  }
  return <ManagementPage />;
}
