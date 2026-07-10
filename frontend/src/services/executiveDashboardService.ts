import { env } from "@/config/env";
import { getApiData } from "@/services/api/httpClient";
import { getAccessToken } from "@/stores/authStore";
import type {
  ExecutiveDashboardData,
  ExecutiveDashboardFilters,
} from "@/types/api/executiveDashboard";

function toQueryString(filters: ExecutiveDashboardFilters): string {
  const params = new URLSearchParams();
  if (filters.from) params.set("from", filters.from);
  if (filters.to) params.set("to", filters.to);
  if (filters.district) params.set("district", filters.district);
  if (filters.station) params.set("station", filters.station);
  if (filters.officer) params.set("officer", filters.officer);
  if (filters.vehicle_type) params.set("vehicle_type", filters.vehicle_type);
  if (filters.risk_level) params.set("risk_level", filters.risk_level);
  if (filters.brand) params.set("brand", filters.brand);
  const query = params.toString();
  return query ? `?${query}` : "";
}

export const executiveDashboardService = {
  getDashboard(filters: ExecutiveDashboardFilters = {}): Promise<ExecutiveDashboardData> {
    return getApiData<ExecutiveDashboardData>(`/v1/dashboard/executive${toQueryString(filters)}`);
  },
  async exportDashboard(
    exportFormat: "pdf" | "csv" | "excel",
    filters: ExecutiveDashboardFilters = {},
  ): Promise<void> {
    const base = env.apiBaseUrl.replace(/\/$/, "");
    const token = getAccessToken();
    const response = await fetch(
      `${base}/v1/dashboard/executive/export/${exportFormat}${toQueryString(filters)}`,
      {
        headers: token ? { Authorization: `Bearer ${token}` } : undefined,
      },
    );
    if (!response.ok) {
      throw new Error(`Export failed with status ${response.status}`);
    }
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    const disposition = response.headers.get("Content-Disposition") ?? "";
    const match = disposition.match(/filename="([^"]+)"/);
    link.download = match?.[1] ?? `executive-command-center.${exportFormat === "excel" ? "xlsx" : exportFormat}`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  },
};
