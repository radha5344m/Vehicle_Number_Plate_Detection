import { useEffect, useState } from "react";
import { stationAdminService } from "@/services/stationAdminService";
import type {
  StationAdminAnalyticsData,
  StationAdminDashboardData,
  StationAdminOfficerItem,
  StationAdminOfficerList,
  StationAdminProfileData,
  StationAdminNotification,
} from "@/types/api/stationAdmin";
import type { InvestigationReportsData, InvestigationReportsFilters } from "@/types/api/investigationReports";

export function useStationAdminDashboard() {
  const [data, setData] = useState<StationAdminDashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    stationAdminService.getDashboard().then(setData).catch((err) => setError(err instanceof Error ? err.message : "Failed to load dashboard")).finally(() => setLoading(false));
  }, []);
  return { data, loading, error };
}

export function useStationOfficers(initialFilters: { search?: string; status?: string; rank?: string; page?: number; page_size?: number } = { page: 1, page_size: 20 }) {
  const [filters, setFilters] = useState(initialFilters);
  const [data, setData] = useState<StationAdminOfficerList | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);
  useEffect(() => {
    setLoading(true);
    stationAdminService.getOfficers(filters).then(setData).catch((err) => setError(err instanceof Error ? err.message : "Failed to load officers")).finally(() => setLoading(false));
  }, [filters, refreshKey]);
  return { data, loading, error, filters, setFilters, refresh: () => setRefreshKey((value) => value + 1) };
}

export function useStationInvestigations(initialFilters: InvestigationReportsFilters = { page: 1, page_size: 20, sort_by: "scanned_at", sort_desc: true }) {
  const [filters, setFilters] = useState(initialFilters);
  const [data, setData] = useState<InvestigationReportsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);
  useEffect(() => {
    setLoading(true);
    stationAdminService.getInvestigations(filters).then(setData).catch((err) => setError(err instanceof Error ? err.message : "Failed to load investigations")).finally(() => setLoading(false));
  }, [filters, refreshKey]);
  return { data, loading, error, filters, setFilters, refresh: () => setRefreshKey((value) => value + 1) };
}

export function useStationReports(initialFilters: InvestigationReportsFilters = { page: 1, page_size: 20, sort_by: "scanned_at", sort_desc: true }) {
  const [filters, setFilters] = useState(initialFilters);
  const [data, setData] = useState<InvestigationReportsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);
  useEffect(() => {
    setLoading(true);
    stationAdminService.getReports(filters).then(setData).catch((err) => setError(err instanceof Error ? err.message : "Failed to load reports")).finally(() => setLoading(false));
  }, [filters, refreshKey]);
  return { data, loading, error, filters, setFilters, setPage: (page: number) => setFilters((current) => ({ ...current, page })), refresh: () => setRefreshKey((value) => value + 1) };
}

export function useStationAnalytics(initialFilters: { from?: string; to?: string } = {}) {
  const [filters, setFilters] = useState(initialFilters);
  const [data, setData] = useState<StationAdminAnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    setLoading(true);
    stationAdminService.getAnalytics(filters).then(setData).catch((err) => setError(err instanceof Error ? err.message : "Failed to load analytics")).finally(() => setLoading(false));
  }, [filters]);
  return { data, loading, error, filters, setFilters };
}

export function useStationNotifications(limit = 20) {
  const [items, setItems] = useState<StationAdminNotification[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    stationAdminService.getNotifications(limit).then((data) => setItems(data.items)).catch((err) => setError(err instanceof Error ? err.message : "Failed to load notifications")).finally(() => setLoading(false));
  }, [limit]);
  return { items, loading, error };
}

export function useStationProfile() {
  const [data, setData] = useState<StationAdminProfileData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);
  useEffect(() => {
    stationAdminService.getProfile().then(setData).catch((err) => setError(err instanceof Error ? err.message : "Failed to load profile")).finally(() => setLoading(false));
  }, [refreshKey]);
  return { data, loading, error, refresh: () => setRefreshKey((value) => value + 1) };
}
