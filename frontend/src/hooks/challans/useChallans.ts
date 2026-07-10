import { useCallback, useEffect, useState } from "react";

import { challansService } from "@/services/challansService";
import type {
  ChallanAnalyticsData,
  ChallanMutationData,
  ChallansFilters,
  ChallansListData,
  CreateChallanPayload,
  VehicleChallanSearchData,
  ViolationMaster,
} from "@/types/api/challans";

export function useViolationMaster() {
  const [violations, setViolations] = useState<ViolationMaster[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    challansService
      .listViolations()
      .then((items) => {
        if (!cancelled) setViolations(items);
      })
      .catch(() => {
        if (!cancelled) setError("Failed to load violation types");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return { violations, loading, error };
}

export function useChallanAnalytics() {
  const [data, setData] = useState<ChallanAnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    challansService
      .getAnalytics()
      .then((result) => {
        if (!cancelled) setData(result);
      })
      .catch(() => {
        if (!cancelled) setError("Failed to load challan analytics");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [refreshKey]);

  return { data, loading, error, refresh: () => setRefreshKey((v) => v + 1) };
}

export function useChallansList(initialFilters: ChallansFilters) {
  const [filters, setFilters] = useState<ChallansFilters>(initialFilters);
  const [data, setData] = useState<ChallansListData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    challansService
      .listChallans(filters)
      .then((result) => {
        if (!cancelled) setData(result);
      })
      .catch(() => {
        if (!cancelled) setError("Failed to load challans");
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
    setPage: (page: number) => setFilters((current) => ({ ...current, page })),
    refresh: () => setRefreshKey((v) => v + 1),
  };
}

export function useVehicleChallanSearch() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<VehicleChallanSearchData | null>(null);

  const search = useCallback(async (registrationNumber: string) => {
    setLoading(true);
    setError(null);
    try {
      const data = await challansService.searchVehicle(registrationNumber);
      setResult(data);
      return data;
    } catch {
      setError("Vehicle search failed");
      setResult(null);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setResult(null);
    setError(null);
  }, []);

  return { result, loading, error, search, reset };
}

export function useCreateChallan() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const create = useCallback(async (payload: CreateChallanPayload): Promise<ChallanMutationData | null> => {
    setLoading(true);
    setError(null);
    try {
      return await challansService.createChallan(payload);
    } catch {
      setError("Failed to issue challan");
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  return { create, loading, error };
}
