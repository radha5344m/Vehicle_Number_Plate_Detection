import { env } from "@/config/env";
import { getAccessToken } from "@/stores/authStore";
import { getApiData } from "@/services/api/httpClient";
import type { InvestigationReportsData, InvestigationReportsFilters } from "@/types/api/investigationReports";

function toQueryString(filters: InvestigationReportsFilters): string {
  const params = new URLSearchParams();
  if (filters.from) params.set("from", filters.from);
  if (filters.to) params.set("to", filters.to);
  if (filters.search) params.set("search", filters.search);
  if (filters.officer) params.set("officer", filters.officer);
  if (filters.police_station) params.set("police_station", filters.police_station);
  if (filters.district) params.set("district", filters.district);
  if (filters.risk_level) params.set("risk_level", filters.risk_level);
  if (filters.vehicle_type) params.set("vehicle_type", filters.vehicle_type);
  if (filters.vehicle_brand) params.set("vehicle_brand", filters.vehicle_brand);
  if (filters.registration_number) params.set("registration_number", filters.registration_number);
  if (filters.owner_name) params.set("owner_name", filters.owner_name);
  if (filters.verification_status) params.set("verification_status", filters.verification_status);
  if (filters.investigation_status) params.set("investigation_status", filters.investigation_status);
  if (filters.ai_confidence_min != null) params.set("ai_confidence_min", String(filters.ai_confidence_min));
  if (filters.ai_confidence_max != null) params.set("ai_confidence_max", String(filters.ai_confidence_max));
  if (filters.page) params.set("page", String(filters.page));
  if (filters.page_size) params.set("page_size", String(filters.page_size));
  if (filters.sort_by) params.set("sort_by", filters.sort_by);
  if (filters.sort_desc != null) params.set("sort_desc", String(filters.sort_desc));
  const query = params.toString();
  return query ? `?${query}` : "";
}

async function downloadBinary(path: string, filename: string): Promise<void> {
  const base = env.apiBaseUrl.replace(/\/$/, "");
  const token = getAccessToken();
  const headers: Record<string, string> = {};
  if (token) headers.Authorization = `Bearer ${token}`;
  const response = await fetch(`${base}${path}`, { headers });
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  const blob = await response.blob();
  const objectUrl = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = objectUrl;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(objectUrl);
}

export const investigationReportsService = {
  getReports(filters: InvestigationReportsFilters = {}): Promise<InvestigationReportsData> {
    return getApiData<InvestigationReportsData>(
      `/v1/investigation-reports${toQueryString(filters)}`,
    );
  },

  exportPdf(filters: InvestigationReportsFilters = {}): Promise<void> {
    return downloadBinary(
      `/v1/investigation-reports/export/pdf${toQueryString(filters)}`,
      "department-investigation-report.pdf",
    );
  },

  exportCsv(filters: InvestigationReportsFilters = {}): Promise<void> {
    return downloadBinary(
      `/v1/investigation-reports/export/csv${toQueryString(filters)}`,
      "department-investigation-report.csv",
    );
  },

  exportExcel(filters: InvestigationReportsFilters = {}): Promise<void> {
    return downloadBinary(
      `/v1/investigation-reports/export/excel${toQueryString(filters)}`,
      "department-investigation-report.xlsx",
    );
  },
};
