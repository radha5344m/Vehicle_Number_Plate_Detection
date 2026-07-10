import { Navigate, useLocation } from "react-router-dom";
import { isAuthenticated } from "@/stores/authStore";
import { PATHS } from "@/routes/paths";
import type { ReactNode } from "react";

interface AuthGuardProps {
  children: ReactNode;
}

export function AuthGuard({ children }: AuthGuardProps) {
  const location = useLocation();

  if (!isAuthenticated()) {
    const redirect = encodeURIComponent(location.pathname);
    return <Navigate to={`${PATHS.LOGIN}?redirect=${redirect}`} replace />;
  }

  return children;
}
