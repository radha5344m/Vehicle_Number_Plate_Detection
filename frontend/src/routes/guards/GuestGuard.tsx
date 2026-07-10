import { Navigate } from "react-router-dom";
import { isAuthenticated } from "@/stores/authStore";
import { getStoredHomePath } from "@/hooks/auth/useAuth";
import type { ReactNode } from "react";

interface GuestGuardProps {
  children: ReactNode;
}

export function GuestGuard({ children }: GuestGuardProps) {
  if (isAuthenticated()) {
    return <Navigate to={getStoredHomePath()} replace />;
  }

  return children;
}
