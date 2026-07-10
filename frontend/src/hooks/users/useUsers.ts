import { useEffect, useState } from "react";

import { getUserFiltersValidationError, sanitizeUserFilters } from "@/lib/userFilters";
import { usersService } from "@/services/usersService";
import type { UserFilters, UsersList } from "@/types/api/users";

interface UseUsersResult {
  data: UsersList | null;
  loading: boolean;
  error: string | null;
  filters: UserFilters;
  setFilters: (filters: UserFilters) => void;
  setPage: (page: number) => void;
  refresh: () => void;
}

export function useUsers(
  initialFilters: UserFilters = { page: 1, page_size: 20, sort_by: "created_at", sort_desc: true },
  enabled = true,
): UseUsersResult {
  const [filters, setFiltersState] = useState<UserFilters>(() => sanitizeUserFilters(initialFilters));
  const [data, setData] = useState<UsersList | null>(null);
  const [loading, setLoading] = useState(enabled);
  const [error, setError] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    if (!enabled) {
      setLoading(false);
      setData(null);
      setError(null);
      return;
    }

    const sanitized = sanitizeUserFilters(filters);
    const validationError = getUserFiltersValidationError(filters);
    if (validationError) {
      const healed =
        sanitized.created_from !== filters.created_from
        || sanitized.created_to !== filters.created_to
        || sanitized.page !== filters.page
        || sanitized.page_size !== filters.page_size;
      if (healed) {
        setFiltersState(sanitized);
        return;
      }
      setLoading(false);
      setError(validationError);
      setData(null);
      return;
    }

    let cancelled = false;
    setLoading(true);
    setError(null);

    usersService
      .list(sanitized)
      .then((result) => {
        if (!cancelled) setData(result);
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : "Failed to load users");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [enabled, filters, refreshKey]);

  return {
    data,
    loading,
    error,
    filters,
    setFilters: (next) => setFiltersState(sanitizeUserFilters(next)),
    setPage: (page) => setFiltersState((current) => sanitizeUserFilters({ ...current, page: Math.max(1, page) })),
    refresh: () => setRefreshKey((value) => value + 1),
  };
}
