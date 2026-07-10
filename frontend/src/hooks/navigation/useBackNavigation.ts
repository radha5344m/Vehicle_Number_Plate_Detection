import { useCallback } from "react";
import { useNavigate } from "react-router-dom";

import { resolveHomePathForRole } from "@/hooks/auth/useAuth";
import { getStoredRole } from "@/stores/authStore";

function canNavigateBack(): boolean {
  const historyIndex = window.history.state?.idx;
  return typeof historyIndex === "number" && historyIndex > 0;
}

export function useBackNavigation() {
  const navigate = useNavigate();

  return useCallback(() => {
    if (canNavigateBack()) {
      navigate(-1);
      return;
    }
    navigate(resolveHomePathForRole(getStoredRole()));
  }, [navigate]);
}
