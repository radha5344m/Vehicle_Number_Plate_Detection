import { useEffect, useMemo, useState } from "react";
import { executiveDashboardService } from "@/services/executiveDashboardService";
import type {
  ExecutiveDashboardData,
  ExecutiveDashboardFilters,
} from "@/types/api/executiveDashboard";

interface UseExecutiveDashboardResult {
  data: ExecutiveDashboardData | null;
  loading: boolean;
  error: string | null;
  filters: ExecutiveDashboardFilters;
  setFilters: (filters: ExecutiveDashboardFilters) => void;
  refresh: () => void;
  exportDashboard: (format: "pdf" | "csv" | "excel") => Promise<void>;
}

export function useExecutiveDashboard(
  initialFilters: ExecutiveDashboardFilters = {},
): UseExecutiveDashboardResult {
  const [filters, setFilters] = useState<ExecutiveDashboardFilters>(initialFilters);
  const [data, setData] = useState<ExecutiveDashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    executiveDashboardService
      .getDashboard(filters)
      .then((result) => {
        if (!cancelled) setData(result);
      })
      .catch(() => {
        if (!cancelled) setError("Failed to load Executive Command Center");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [filters, refreshKey]);

  const refresh = () => setRefreshKey((value) => value + 1);

  useEffect(() => {
    if (!data) return;
    const interval = window.setInterval(refresh, data.connection_status.auto_refresh_seconds * 1000);
    return () => window.clearInterval(interval);
  }, [data]);

  return useMemo(
    () => ({
      data,
      loading,
      error,
      filters,
      setFilters,
      refresh,
      exportDashboard: (format) => executiveDashboardService.exportDashboard(format, filters),
    }),
    [data, loading, error, filters],
  );
}
