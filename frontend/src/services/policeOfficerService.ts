import { env } from "@/config/env";
import { getApiData, patchApiData, postApiData } from "@/services/api/httpClient";
import { getAccessToken } from "@/stores/authStore";
import type {
  ActionMessage,
  PoliceOfficerDashboardData,
  PoliceOfficerNotificationsData,
  PoliceOfficerProfileData,
  PoliceOfficerReportsData,
  PoliceOfficerReportsFilters,
} from "@/types/api/policeOfficer";

function toQueryString(
  filters: Record<string, string | number | boolean | undefined>,
): string {
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

function reportsQuery(filters: PoliceOfficerReportsFilters): string {
  return toQueryString({
    from: filters.from,
    to: filters.to,
    search: filters.search,
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

export const policeOfficerService = {
  getDashboard(): Promise<PoliceOfficerDashboardData> {
    return getApiData<PoliceOfficerDashboardData>("/v1/police-officer/dashboard");
  },
  getInvestigations(filters: PoliceOfficerReportsFilters = {}): Promise<PoliceOfficerReportsData> {
    return getApiData<PoliceOfficerReportsData>(
      `/v1/police-officer/investigations${reportsQuery(filters)}`,
    );
  },
  getReports(filters: PoliceOfficerReportsFilters = {}): Promise<PoliceOfficerReportsData> {
    return getApiData<PoliceOfficerReportsData>(
      `/v1/police-officer/reports${reportsQuery(filters)}`,
    );
  },
  exportPdf(filters: PoliceOfficerReportsFilters = {}): Promise<void> {
    return downloadBinary(
      `/v1/police-officer/reports/export/pdf${reportsQuery(filters)}`,
      "my-investigation-reports.pdf",
    );
  },
  exportCsv(filters: PoliceOfficerReportsFilters = {}): Promise<void> {
    return downloadBinary(
      `/v1/police-officer/reports/export/csv${reportsQuery(filters)}`,
      "my-investigation-reports.csv",
    );
  },
  exportExcel(filters: PoliceOfficerReportsFilters = {}): Promise<void> {
    return downloadBinary(
      `/v1/police-officer/reports/export/excel${reportsQuery(filters)}`,
      "my-investigation-reports.xlsx",
    );
  },
  getNotifications(limit = 20): Promise<PoliceOfficerNotificationsData> {
    return getApiData<PoliceOfficerNotificationsData>(
      `/v1/police-officer/notifications${toQueryString({ limit })}`,
    );
  },
  getProfile(): Promise<PoliceOfficerProfileData> {
    return getApiData<PoliceOfficerProfileData>("/v1/police-officer/profile");
  },
  changePassword(current_password: string, new_password: string): Promise<ActionMessage> {
    return postApiData<ActionMessage>("/v1/police-officer/profile/change-password", {
      current_password,
      new_password,
    });
  },
  updateProfile(body: {
    first_name: string;
    last_name: string;
    email: string;
    phone_number?: string;
    employee_id: string;
  }): Promise<PoliceOfficerProfileData> {
    return patchApiData<PoliceOfficerProfileData>("/v1/police-officer/profile", body);
  },
};
