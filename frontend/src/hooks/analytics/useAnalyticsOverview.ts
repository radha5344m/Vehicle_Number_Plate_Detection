import { useEffect, useState } from "react";
import { analyticsService } from "@/services/analyticsService";
import type { AnalyticsFilters, AnalyticsOverview } from "@/types/api/analytics";

interface UseAnalyticsOverviewResult {
  data: AnalyticsOverview | null;
  loading: boolean;
  error: string | null;
  filters: AnalyticsFilters;
  setFilters: (filters: AnalyticsFilters) => void;
  refresh: () => void;
}

export function useAnalyticsOverview(initialFilters: AnalyticsFilters = {}): UseAnalyticsOverviewResult {
  const [filters, setFilters] = useState<AnalyticsFilters>(initialFilters);
  const [data, setData] = useState<AnalyticsOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);

    analyticsService
      .getOverview(filters)
      .then((overview) => {
        if (!cancelled) setData(overview);
      })
      .catch(() => {
        if (!cancelled) setError("Failed to load analytics");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [filters, refreshKey]);

  return {
    data,
    loading,
    error,
    filters,
    setFilters,
    refresh: () => setRefreshKey((value) => value + 1),
  };
}
