import { Navigate } from "react-router-dom";

import { LandingPage } from "@/pages/home/LandingPage";
import { LoginPage } from "@/pages/auth/LoginPage";
import { ScanHistoryPage } from "@/pages/history/ScanHistoryPage";
import { ManagementRouterPage } from "@/pages/management/ManagementRouterPage";
import { UsersPage } from "@/pages/users/UsersPage";
import { PoliceStationsPage } from "@/pages/stations/PoliceStationsPage";
import { NotificationsPage } from "@/pages/notifications/NotificationsPage";
import { ProfilePage } from "@/pages/profile/ProfilePage";
import { StationInvestigationsPage } from "@/pages/stationAdmin/StationInvestigationsPage";
import { InvestigationReportsPage } from "@/pages/reports/InvestigationReportsPage";
import { InvestigationReportPage } from "@/pages/reports/InvestigationReportPage";
import { AnalyticsPage } from "@/pages/analytics/AnalyticsPage";
import { ChallansPage } from "@/pages/challans/ChallansPage";
import { VehicleVerificationWorkflowPage } from "@/pages/workflow/VehicleVerificationWorkflowPage";
import { DashboardPage } from "@/pages/dashboard/DashboardPage";
import { AccessDeniedPage } from "@/pages/errors/AccessDeniedPage";
import { NotFoundPage } from "@/pages/errors/NotFoundPage";
import { AuthGuard } from "@/routes/guards/AuthGuard";
import { GuestGuard } from "@/routes/guards/GuestGuard";
import { PermissionGuard } from "@/routes/guards/PermissionGuard";
import { PATHS } from "@/routes/paths";
import { getStoredHomePath } from "@/hooks/auth/useAuth";
import type { RouteObject } from "react-router-dom";

export const routes: RouteObject[] = [
  { path: PATHS.HOME, element: <LandingPage /> },
  {
    path: PATHS.LOGIN,
    element: (
      <GuestGuard>
        <LoginPage />
      </GuestGuard>
    ),
  },
  { path: PATHS.ACCESS_DENIED, element: <AccessDeniedPage /> },
  {
    path: PATHS.ADMIN_DASHBOARD,
    element: (
      <AuthGuard>
        <PermissionGuard requiredPermissions={["dashboard"]} allowedRoles={["SUPER_ADMIN"]}>
          <DashboardPage />
        </PermissionGuard>
      </AuthGuard>
    ),
  },
  {
    path: PATHS.STATION_DASHBOARD,
    element: (
      <AuthGuard>
        <PermissionGuard requiredPermissions={["dashboard"]} allowedRoles={["STATION_ADMIN"]}>
          <DashboardPage />
        </PermissionGuard>
      </AuthGuard>
    ),
  },
  {
    path: PATHS.OFFICER_DASHBOARD,
    element: (
      <AuthGuard>
        <PermissionGuard requiredPermissions={["dashboard"]} allowedRoles={["POLICE_OFFICER"]}>
          <DashboardPage />
        </PermissionGuard>
      </AuthGuard>
    ),
  },
  {
    path: PATHS.APP,
    element: (
      <AuthGuard>
        <Navigate to={getStoredHomePath()} replace />
      </AuthGuard>
    ),
  },
  {
    path: PATHS.DASHBOARD,
    element: (
      <AuthGuard>
        <PermissionGuard requiredPermissions={["dashboard"]}>
          <DashboardPage />
        </PermissionGuard>
      </AuthGuard>
    ),
  },
  {
    path: PATHS.WORKFLOW,
    element: (
      <AuthGuard>
        <PermissionGuard requiredPermissions={["vehicle_verification"]}>
          <VehicleVerificationWorkflowPage />
        </PermissionGuard>
      </AuthGuard>
    ),
  },
  {
    path: PATHS.HISTORY_SCANS,
    element: (
      <AuthGuard>
        <PermissionGuard requiredPermissions={["investigation_history"]}>
          <ScanHistoryPage />
        </PermissionGuard>
      </AuthGuard>
    ),
  },
  {
    path: PATHS.STATION_INVESTIGATIONS,
    element: (
      <AuthGuard>
        <PermissionGuard requiredPermissions={["investigation_history"]} allowedRoles={["STATION_ADMIN"]}>
          <StationInvestigationsPage />
        </PermissionGuard>
      </AuthGuard>
    ),
  },
  {
    path: PATHS.MANAGEMENT,
    element: (
      <AuthGuard>
        <PermissionGuard
          allowedRoles={["SUPER_ADMIN", "STATION_ADMIN"]}
          requiredPermissions={["users", "stations", "officers"]}
          requireAnyPermission
        >
          <ManagementRouterPage />
        </PermissionGuard>
      </AuthGuard>
    ),
  },
  {
    path: PATHS.USERS,
    element: (
      <AuthGuard>
        <PermissionGuard requiredPermissions={["users"]} allowedRoles={["SUPER_ADMIN"]}>
          <Navigate to={PATHS.MANAGEMENT} replace />
        </PermissionGuard>
      </AuthGuard>
    ),
  },
  {
    path: PATHS.STATIONS,
    element: (
      <AuthGuard>
        <PermissionGuard requiredPermissions={["stations"]} allowedRoles={["SUPER_ADMIN"]}>
          <Navigate to={PATHS.MANAGEMENT} replace />
        </PermissionGuard>
      </AuthGuard>
    ),
  },
  {
    path: PATHS.OFFICERS,
    element: (
      <AuthGuard>
        <PermissionGuard requiredPermissions={["officers"]} allowedRoles={["STATION_ADMIN"]}>
          <Navigate to={PATHS.MANAGEMENT} replace />
        </PermissionGuard>
      </AuthGuard>
    ),
  },
  {
    path: PATHS.NOTIFICATIONS,
    element: (
      <AuthGuard>
        <PermissionGuard allowedRoles={["SUPER_ADMIN", "STATION_ADMIN", "POLICE_OFFICER"]}>
          <NotificationsPage />
        </PermissionGuard>
      </AuthGuard>
    ),
  },
  {
    path: PATHS.PROFILE,
    element: (
      <AuthGuard>
        <PermissionGuard requiredPermissions={["profile"]}>
          <ProfilePage />
        </PermissionGuard>
      </AuthGuard>
    ),
  },
  {
    path: PATHS.REPORTS,
    element: (
      <AuthGuard>
        <PermissionGuard requiredPermissions={["reports"]}>
          <InvestigationReportsPage />
        </PermissionGuard>
      </AuthGuard>
    ),
  },
  {
    path: PATHS.REPORTS_MANUAL,
    element: (
      <AuthGuard>
        <PermissionGuard requiredPermissions={["reports"]}>
          <InvestigationReportPage />
        </PermissionGuard>
      </AuthGuard>
    ),
  },
  {
    path: PATHS.ECHALLANS,
    element: (
      <AuthGuard>
        <PermissionGuard requiredPermissions={["challans"]}>
          <ChallansPage />
        </PermissionGuard>
      </AuthGuard>
    ),
  },
  {
    path: PATHS.ANALYTICS,
    element: (
      <AuthGuard>
        <PermissionGuard requiredPermissions={["analytics"]} allowedRoles={["SUPER_ADMIN", "STATION_ADMIN"]}>
          <AnalyticsPage />
        </PermissionGuard>
      </AuthGuard>
    ),
  },
  { path: "*", element: <NotFoundPage /> },
];
