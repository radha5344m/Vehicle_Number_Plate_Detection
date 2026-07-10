import type { AuthSession, OfficerSummary, StationSummary } from "@/types/api/auth";

const ACCESS_TOKEN_KEY = "sentinel_access_token";
const REFRESH_TOKEN_KEY = "sentinel_refresh_token";
const SESSION_KEY = "sentinel_session";

export function getAccessToken(): string | null {
  return sessionStorage.getItem(ACCESS_TOKEN_KEY);
}

export function getRefreshToken(): string | null {
  return sessionStorage.getItem(REFRESH_TOKEN_KEY);
}

export function getStoredOfficer(): OfficerSummary | null {
  const raw = sessionStorage.getItem(SESSION_KEY);
  if (!raw) return null;
  return (JSON.parse(raw) as AuthSession).officer;
}

export function getAuthSession(): AuthSession | null {
  const raw = sessionStorage.getItem(SESSION_KEY);
  if (!raw) return null;
  return JSON.parse(raw) as AuthSession;
}

export function getStoredRole(): string | null {
  return getAuthSession()?.role ?? null;
}

export function getStoredPermissions(): string[] {
  return getAuthSession()?.permissions ?? [];
}

export function getStoredStation(): StationSummary | null {
  return getAuthSession()?.station ?? null;
}

export function isAuthenticated(): boolean {
  return Boolean(getAccessToken());
}

export function setAuth(
  accessToken: string,
  refreshToken: string,
  officer: OfficerSummary,
  role: string,
  permissions: string[],
  station: StationSummary,
): void {
  sessionStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
  sessionStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
  sessionStorage.setItem(
    SESSION_KEY,
    JSON.stringify({ officer, role, permissions, station } satisfies AuthSession),
  );
}

export function clearAuth(): void {
  sessionStorage.removeItem(ACCESS_TOKEN_KEY);
  sessionStorage.removeItem(REFRESH_TOKEN_KEY);
  sessionStorage.removeItem(SESSION_KEY);
}

export function updateStoredOfficer(partial: Partial<OfficerSummary>): void {
  const accessToken = getAccessToken();
  const refreshToken = getRefreshToken();
  const session = getAuthSession();
  if (!accessToken || !refreshToken || !session) return;

  setAuth(
    accessToken,
    refreshToken,
    { ...session.officer, ...partial },
    session.role,
    session.permissions,
    session.station,
  );
}
