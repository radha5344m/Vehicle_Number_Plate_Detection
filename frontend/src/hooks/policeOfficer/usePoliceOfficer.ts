import { useEffect, useState } from "react";

import { policeOfficerService } from "@/services/policeOfficerService";
import type {
  PoliceOfficerDashboardData,
  PoliceOfficerNotification,
  PoliceOfficerProfileData,
  PoliceOfficerReportsData,
  PoliceOfficerReportsFilters,
} from "@/types/api/policeOfficer";

export function usePoliceOfficerDashboard() {
  const [data, setData] = useState<PoliceOfficerDashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    policeOfficerService
      .getDashboard()
      .then(setData)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load dashboard"))
      .finally(() => setLoading(false));
  }, []);

  return { data, loading, error };
}

function useOfficerReportsBase(
  loader: (filters: PoliceOfficerReportsFilters) => Promise<PoliceOfficerReportsData>,
  initialFilters: PoliceOfficerReportsFilters,
) {
  const [filters, setFilters] = useState(initialFilters);
  const [data, setData] = useState<PoliceOfficerReportsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    setLoading(true);
    loader(filters)
      .then(setData)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load investigations"))
      .finally(() => setLoading(false));
  }, [filters, refreshKey, loader]);

  return {
    data,
    loading,
    error,
    filters,
    setFilters,
    setPage: (page: number) => setFilters((current) => ({ ...current, page })),
    refresh: () => setRefreshKey((value) => value + 1),
  };
}

export function usePoliceOfficerInvestigations(
  initialFilters: PoliceOfficerReportsFilters = {
    page: 1,
    page_size: 20,
    sort_by: "scanned_at",
    sort_desc: true,
  },
) {
  return useOfficerReportsBase(policeOfficerService.getInvestigations, initialFilters);
}

export function usePoliceOfficerReports(
  initialFilters: PoliceOfficerReportsFilters = {
    page: 1,
    page_size: 20,
    sort_by: "scanned_at",
    sort_desc: true,
  },
) {
  return useOfficerReportsBase(policeOfficerService.getReports, initialFilters);
}

export function usePoliceOfficerNotifications(limit = 20) {
  const [items, setItems] = useState<PoliceOfficerNotification[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    policeOfficerService
      .getNotifications(limit)
      .then((data) => setItems(data.items))
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load notifications"))
      .finally(() => setLoading(false));
  }, [limit]);

  return { items, loading, error };
}

export function usePoliceOfficerProfile() {
  const [data, setData] = useState<PoliceOfficerProfileData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    policeOfficerService
      .getProfile()
      .then(setData)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load profile"))
      .finally(() => setLoading(false));
  }, [refreshKey]);

  return { data, loading, error, refresh: () => setRefreshKey((value) => value + 1) };
}
