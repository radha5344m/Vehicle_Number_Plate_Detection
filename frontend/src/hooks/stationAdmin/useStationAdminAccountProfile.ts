import { useCallback, useEffect, useState } from "react";
import { stationAdminAccountService } from "@/services/stationAdminAccountService";
import type { AccountProfileData } from "@/types/api/accountProfile";

export function useStationAdminAccountProfile() {
  const [data, setData] = useState<AccountProfileData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(() => {
    setLoading(true);
    setError(null);
    stationAdminAccountService
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
