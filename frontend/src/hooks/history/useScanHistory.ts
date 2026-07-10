import { useCallback, useEffect, useState } from "react";
import { historyService } from "@/services/historyService";
import type { ScanHistoryFilters, ScanHistoryItem } from "@/types/api/history";

interface UseScanHistoryResult {
  items: ScanHistoryItem[];
  page: number;
  totalPages: number;
  totalItems: number;
  loading: boolean;
  error: string | null;
  filters: ScanHistoryFilters;
  setFilters: (filters: ScanHistoryFilters) => void;
  setPage: (page: number) => void;
  refresh: () => void;
}

export function useScanHistory(initialFilters: ScanHistoryFilters = {}): UseScanHistoryResult {
  const [filters, setFilters] = useState<ScanHistoryFilters>(initialFilters);
  const [page, setPage] = useState(1);
  const [items, setItems] = useState<ScanHistoryItem[]>([]);
  const [totalPages, setTotalPages] = useState(0);
  const [totalItems, setTotalItems] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  const refresh = useCallback(() => {
    setRefreshKey((value) => value + 1);
  }, []);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);

    historyService
      .getScanHistory({ ...filters, page, page_size: filters.page_size ?? 20 })
      .then((data) => {
        if (!cancelled) {
          setItems(data.items);
          setTotalPages(data.pagination.total_pages);
          setTotalItems(data.pagination.total_items);
        }
      })
      .catch(() => {
        if (!cancelled) setError("Failed to load scan history");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [filters, page, refreshKey]);

  return {
    items,
    page,
    totalPages,
    totalItems,
    loading,
    error,
    filters,
    setFilters,
    setPage,
    refresh,
  };
}
