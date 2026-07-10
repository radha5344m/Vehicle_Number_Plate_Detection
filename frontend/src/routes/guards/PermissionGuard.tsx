import type { ReactNode } from "react";
import { Navigate, useLocation } from "react-router-dom";

import { hasAnyRole, hasPermission, type AppRole } from "@/lib/rbac";
import { isAuthenticated } from "@/stores/authStore";
import { PATHS } from "@/routes/paths";

interface PermissionGuardProps {
  children: ReactNode;
  requiredPermissions?: string[];
  allowedRoles?: AppRole[];
  requireAnyPermission?: boolean;
}

export function PermissionGuard({
  children,
  requiredPermissions,
  allowedRoles,
  requireAnyPermission = false,
}: PermissionGuardProps) {
  const location = useLocation();

  if (!isAuthenticated()) {
    const redirect = encodeURIComponent(location.pathname);
    return <Navigate to={`${PATHS.LOGIN}?redirect=${redirect}`} replace />;
  }

  const permissionAllowed =
    !requiredPermissions ||
    requiredPermissions.length === 0 ||
    (requireAnyPermission
      ? requiredPermissions.some((permission) => hasPermission(permission))
      : requiredPermissions.every((permission) => hasPermission(permission)));
  const roleAllowed = !allowedRoles || hasAnyRole(allowedRoles);

  if (!permissionAllowed || !roleAllowed) {
    return <Navigate to={PATHS.ACCESS_DENIED} replace state={{ from: location.pathname }} />;
  }

  return children;
}
