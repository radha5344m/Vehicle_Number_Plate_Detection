import { useCallback, useEffect, useState } from "react";
import { superAdminService } from "@/services/superAdminService";
import type { AccountProfileData } from "@/types/api/accountProfile";

export function useSuperAdminProfile() {
  const [data, setData] = useState<AccountProfileData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(() => {
    setLoading(true);
    setError(null);
    superAdminService
      .getProfile()
      .then(setData)
      .catch((err) => {
        setError(err instanceof Error ? err.message : "Failed to load profile");
      })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  return {
    data,
    loading,
    error,
    refresh: load,
  };
}
