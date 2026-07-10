import { useEffect, useState } from "react";

import { stationsService } from "@/services/stationsService";
import type { StationFilters, StationsList } from "@/types/api/stations";

interface UseStationsResult {
  data: StationsList | null;
  loading: boolean;
  error: string | null;
  filters: StationFilters;
  setFilters: (filters: StationFilters) => void;
  setPage: (page: number) => void;
  refresh: () => void;
}

export function useStations(
  initialFilters: StationFilters = { page: 1, page_size: 20, sort_by: "created_at", sort_desc: true },
): UseStationsResult {
  const [filters, setFiltersState] = useState<StationFilters>(initialFilters);
  const [data, setData] = useState<StationsList | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);

    stationsService
      .list(filters)
      .then((result) => {
        if (!cancelled) setData(result);
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : "Failed to load stations");
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
    setFilters: (next) => setFiltersState(next),
    setPage: (page) => setFiltersState((current) => ({ ...current, page })),
    refresh: () => setRefreshKey((value) => value + 1),
  };
}
