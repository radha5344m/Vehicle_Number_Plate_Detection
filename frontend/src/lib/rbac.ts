import { getAuthSession } from "@/stores/authStore";
import type { AuthSession } from "@/types/api/auth";

export type AppRole = "SUPER_ADMIN" | "STATION_ADMIN" | "POLICE_OFFICER";

export function getCurrentSession(): AuthSession | null {
  return getAuthSession();
}

export function hasPermission(permission: string, session: AuthSession | null = getCurrentSession()): boolean {
  return session?.permissions.includes(permission) ?? false;
}

export function hasRole(role: AppRole, session: AuthSession | null = getCurrentSession()): boolean {
  return session?.role === role;
}

export function hasAnyRole(
  roles: AppRole[],
  session: AuthSession | null = getCurrentSession(),
): boolean {
  return session !== null && roles.includes(session.role as AppRole);
}
