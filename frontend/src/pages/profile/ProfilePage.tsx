import { hasRole } from "@/lib/rbac";
import { OfficerProfilePage } from "@/pages/policeOfficer/OfficerProfilePage";
import { SuperAdminProfilePage } from "@/pages/superAdmin/SuperAdminProfilePage";
import { StationProfilePage } from "@/pages/stationAdmin/StationProfilePage";

export function ProfilePage() {
  if (hasRole("SUPER_ADMIN")) {
    return <SuperAdminProfilePage />;
  }
  if (hasRole("STATION_ADMIN")) {
    return <StationProfilePage />;
  }
  if (hasRole("POLICE_OFFICER")) {
    return <OfficerProfilePage />;
  }

  return null;
}
