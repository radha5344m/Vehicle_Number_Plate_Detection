import { useEffect, useState } from "react";

import { investigationReportsService } from "@/services/investigationReportsService";
import type {
  InvestigationReportsData,
  InvestigationReportsFilters,
} from "@/types/api/investigationReports";

interface UseInvestigationReportsResult {
  data: InvestigationReportsData | null;
  loading: boolean;
  error: string | null;
  filters: InvestigationReportsFilters;
  setFilters: (filters: InvestigationReportsFilters) => void;
  setPage: (page: number) => void;
  refresh: () => void;
}

export function useInvestigationReports(
  initialFilters: InvestigationReportsFilters = { page: 1, page_size: 20, sort_by: "scanned_at", sort_desc: true },
): UseInvestigationReportsResult {
  const [filters, setFiltersState] = useState<InvestigationReportsFilters>(initialFilters);
  const [data, setData] = useState<InvestigationReportsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);

    investigationReportsService
      .getReports(filters)
      .then((result) => {
        if (!cancelled) setData(result);
      })
      .catch(() => {
        if (!cancelled) setError("Failed to load investigation reports");
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
