import { useCallback, useState } from "react";
import { useNavigate } from "react-router-dom";
import { authService } from "@/services/authService";
import {
  clearAuth,
  getRefreshToken,
  getStoredOfficer,
  getStoredRole,
  isAuthenticated,
  setAuth,
} from "@/stores/authStore";
import type { LoginRequest, OfficerSummary } from "@/types/api/auth";
import { PATHS } from "@/routes/paths";

function resolvePostLoginPath(role: string, redirectTo?: string): string {
  if (redirectTo) return redirectTo;
  if (role === "SUPER_ADMIN") return PATHS.ADMIN_DASHBOARD;
  if (role === "STATION_ADMIN") return PATHS.STATION_DASHBOARD;
  if (role === "POLICE_OFFICER") return PATHS.OFFICER_DASHBOARD;
  return PATHS.DASHBOARD;
}

export function resolveHomePathForRole(role: string | null): string {
  if (role === "SUPER_ADMIN") return PATHS.ADMIN_DASHBOARD;
  if (role === "STATION_ADMIN") return PATHS.STATION_DASHBOARD;
  if (role === "POLICE_OFFICER") return PATHS.OFFICER_DASHBOARD;
  return PATHS.DASHBOARD;
}

export function useAuth() {
  const navigate = useNavigate();
  const [officer, setOfficer] = useState<OfficerSummary | null>(getStoredOfficer());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const login = useCallback(
    async (payload: LoginRequest, redirectTo?: string) => {
      setLoading(true);
      setError(null);
      try {
        const result = await authService.login(payload);
        setAuth(
          result.access_token,
          result.refresh_token,
          result.officer,
          result.role,
          result.permissions,
          result.station,
        );
        setOfficer(result.officer);
        navigate(resolvePostLoginPath(result.role, redirectTo), { replace: true });
      } catch (err) {
        const message = err instanceof Error ? err.message : "Login failed";
        setError(message);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [navigate],
  );

  const logout = useCallback(async () => {
    const refreshToken = getRefreshToken();
    try {
      if (refreshToken && isAuthenticated()) {
        await authService.logout(refreshToken);
      }
    } catch {
      // clear local session even if API call fails
    } finally {
      clearAuth();
      setOfficer(null);
      navigate(PATHS.LOGIN, { replace: true });
    }
  }, [navigate]);

  return {
    officer,
    isAuthenticated: isAuthenticated(),
    loading,
    error,
    login,
    logout,
  };
}

export function getStoredHomePath(): string {
  return resolveHomePathForRole(getStoredRole());
}
