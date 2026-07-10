import { hasRole } from "@/lib/rbac";
import { OfficerNotificationsPage } from "@/pages/policeOfficer/OfficerNotificationsPage";
import { SuperAdminNotificationsPage } from "@/pages/superAdmin/SuperAdminNotificationsPage";
import { StationNotificationsPage } from "@/pages/stationAdmin/StationNotificationsPage";

export function NotificationsPage() {
  if (hasRole("SUPER_ADMIN")) {
    return <SuperAdminNotificationsPage />;
  }
  if (hasRole("POLICE_OFFICER")) {
    return <OfficerNotificationsPage />;
  }

  return <StationNotificationsPage />;
}
