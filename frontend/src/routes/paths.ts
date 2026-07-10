// Public routes — accessible without authentication
export const PUBLIC_PATHS = {
  HOME: "/",
  LOGIN: "/login",
  ACCESS_DENIED: "/403",
} as const;

export const ROLE_PATHS = {
  ADMIN_DASHBOARD: "/admin/dashboard",
  STATION_DASHBOARD: "/station/dashboard",
  OFFICER_DASHBOARD: "/officer/dashboard",
} as const;

// Authenticated routes — Officer Command Center, all namespaced under /app
export const APP_PATHS = {
  APP: "/app",
  DASHBOARD: "/app/dashboard",
  WORKFLOW: "/app/workflow",
  HISTORY_SCANS: "/app/history/scans",
  STATION_INVESTIGATIONS: "/app/station-investigations",
  MANAGEMENT: "/app/management",
  USERS: "/app/users",
  STATIONS: "/app/stations",
  OFFICERS: "/app/officers",
  NOTIFICATIONS: "/app/notifications",
  PROFILE: "/app/profile",
  REPORTS: "/app/reports",
  REPORTS_MANUAL: "/app/reports/manual",
  ANALYTICS: "/app/analytics",
  ECHALLANS: "/app/challans",
  SETTINGS: "/app/settings",
} as const;

export const PATHS = {
  ...PUBLIC_PATHS,
  ...ROLE_PATHS,
  ...APP_PATHS,
} as const;

// Landing target for an authenticated officer.
export const AUTHENTICATED_HOME = APP_PATHS.DASHBOARD;
