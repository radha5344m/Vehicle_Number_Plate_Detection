import { deleteApiData, getApiData, patchApiData, postApiData, putApiData } from "@/services/api/httpClient";
import type {
  ActionMessage,
  CreateOfficerRequest,
  OfficerMutationResult,
  StationAdminAnalyticsData,
  StationAdminDashboardData,
  StationAdminNotification,
  StationAdminOfficerItem,
  StationAdminOfficerList,
  StationAdminProfileData,
  UpdateOfficerRequest,
  UpdateStationDetailsRequest,
} from "@/types/api/stationAdmin";
import type { InvestigationReportsData, InvestigationReportsFilters } from "@/types/api/investigationReports";
import { env } from "@/config/env";
import { getAccessToken } from "@/stores/authStore";

function toQueryString(filters: Record<string, string | number | boolean | undefined>): string {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== "") params.set(key, String(value));
  });
  const query = params.toString();
  return query ? `?${query}` : "";
}

async function downloadBinary(path: string, filename: string): Promise<void> {
  const base = env.apiBaseUrl.replace(/\/$/, "");
  const token = getAccessToken();
  const headers: Record<string, string> = {};
  if (token) headers.Authorization = `Bearer ${token}`;
  const response = await fetch(`${base}${path}`, { headers });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  const blob = await response.blob();
  const objectUrl = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = objectUrl;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(objectUrl);
}

function reportsQuery(filters: InvestigationReportsFilters): string {
  return toQueryString({
    from: filters.from,
    to: filters.to,
    search: filters.search,
    officer: filters.officer,
    risk_level: filters.risk_level,
    district: filters.district,
    vehicle_type: filters.vehicle_type,
    vehicle_brand: filters.vehicle_brand,
    registration_number: filters.registration_number,
    owner_name: filters.owner_name,
    verification_status: filters.verification_status,
    investigation_status: filters.investigation_status,
    ai_confidence_min: filters.ai_confidence_min,
    ai_confidence_max: filters.ai_confidence_max,
    page: filters.page,
    page_size: filters.page_size,
    sort_by: filters.sort_by,
    sort_desc: filters.sort_desc,
  });
}

export const stationAdminService = {
  getDashboard(): Promise<StationAdminDashboardData> {
    return getApiData<StationAdminDashboardData>("/v1/station-admin/dashboard");
  },
  getOfficers(filters: { search?: string; status?: string; rank?: string; page?: number; page_size?: number } = {}): Promise<StationAdminOfficerList> {
    return getApiData<StationAdminOfficerList>(`/v1/station-admin/officers${toQueryString(filters)}`);
  },
  createOfficer(body: CreateOfficerRequest): Promise<OfficerMutationResult> {
    return postApiData<OfficerMutationResult>("/v1/station-admin/officers", body);
  },
  updateOfficer(officerId: string, body: UpdateOfficerRequest): Promise<OfficerMutationResult> {
    return putApiData<OfficerMutationResult>(`/v1/station-admin/officers/${officerId}`, body);
  },
  activateOfficer(officerId: string): Promise<OfficerMutationResult> {
    return postApiData<OfficerMutationResult>(`/v1/station-admin/officers/${officerId}/activate`, {});
  },
  deactivateOfficer(officerId: string): Promise<OfficerMutationResult> {
    return postApiData<OfficerMutationResult>(`/v1/station-admin/officers/${officerId}/deactivate`, {});
  },
  deleteOfficer(officerId: string): Promise<ActionMessage> {
    return deleteApiData<ActionMessage>(`/v1/station-admin/officers/${officerId}`);
  },
  resetOfficerPassword(officerId: string, new_password: string): Promise<ActionMessage> {
    return postApiData<ActionMessage>(`/v1/station-admin/officers/${officerId}/reset-password`, { new_password });
  },
  getInvestigations(filters: InvestigationReportsFilters = {}): Promise<InvestigationReportsData> {
    return getApiData<InvestigationReportsData>(`/v1/station-admin/investigations${reportsQuery(filters)}`);
  },
  getReports(filters: InvestigationReportsFilters = {}): Promise<InvestigationReportsData> {
    return getApiData<InvestigationReportsData>(`/v1/station-admin/reports${reportsQuery(filters)}`);
  },
  exportPdf(filters: InvestigationReportsFilters = {}): Promise<void> {
    return downloadBinary(`/v1/station-admin/reports/export/pdf${reportsQuery(filters)}`, "station-report.pdf");
  },
  exportCsv(filters: InvestigationReportsFilters = {}): Promise<void> {
    return downloadBinary(`/v1/station-admin/reports/export/csv${reportsQuery(filters)}`, "station-report.csv");
  },
  exportExcel(filters: InvestigationReportsFilters = {}): Promise<void> {
    return downloadBinary(`/v1/station-admin/reports/export/excel${reportsQuery(filters)}`, "station-report.xlsx");
  },
  getAnalytics(filters: { from?: string; to?: string } = {}): Promise<StationAdminAnalyticsData> {
    return getApiData<StationAdminAnalyticsData>(`/v1/station-admin/analytics${toQueryString(filters)}`);
  },
  getNotifications(limit = 20): Promise<{ items: StationAdminNotification[] }> {
    return getApiData<{ items: StationAdminNotification[] }>(`/v1/station-admin/notifications?limit=${limit}`);
  },
  getProfile(): Promise<StationAdminProfileData> {
    return getApiData<StationAdminProfileData>("/v1/station-admin/profile");
  },
  updateStation(body: UpdateStationDetailsRequest): Promise<StationAdminProfileData> {
    return patchApiData<StationAdminProfileData>("/v1/station-admin/station", body);
  },
  changePassword(current_password: string, new_password: string): Promise<ActionMessage> {
    return postApiData<ActionMessage>("/v1/station-admin/profile/change-password", { current_password, new_password });
  },
  updateAccountProfile(body: {
    first_name: string;
    last_name: string;
    email: string;
    phone_number?: string;
    employee_id: string;
  }): Promise<StationAdminProfileData> {
    return patchApiData<StationAdminProfileData>("/v1/station-admin/profile", body);
  },
};
