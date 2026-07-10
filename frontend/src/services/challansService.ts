import { env } from "@/config/env";
import { getAccessToken } from "@/stores/authStore";
import { getApiData, postApiData } from "@/services/api/httpClient";
import { monitoredFetch } from "@/services/api/monitoredFetch";
import type {
  ChallanAnalyticsData,
  ChallanMutationData,
  ChallansFilters,
  ChallansListData,
  CreateChallanPayload,
  VehicleChallanSearchData,
  ViolationMaster,
} from "@/types/api/challans";

function toQueryString(filters: ChallansFilters): string {
  const params = new URLSearchParams();
  if (filters.search) params.set("search", filters.search);
  if (filters.registration_number) params.set("registration_number", filters.registration_number);
  if (filters.challan_number) params.set("challan_number", filters.challan_number);
  if (filters.owner_name) params.set("owner_name", filters.owner_name);
  if (filters.officer_id) params.set("officer_id", filters.officer_id);
  if (filters.station_id) params.set("station_id", filters.station_id);
  if (filters.violation_type) params.set("violation_type", filters.violation_type);
  if (filters.payment_status) params.set("payment_status", filters.payment_status);
  if (filters.pending_only) params.set("pending_only", "true");
  if (filters.issued_from) params.set("issued_from", filters.issued_from);
  if (filters.issued_to) params.set("issued_to", filters.issued_to);
  if (filters.page) params.set("page", String(filters.page));
  if (filters.page_size) params.set("page_size", String(filters.page_size));
  const query = params.toString();
  return query ? `?${query}` : "";
}

async function downloadBinary(path: string, filename: string): Promise<void> {
  const base = env.apiBaseUrl.replace(/\/$/, "");
  const token = getAccessToken();
  const headers: Record<string, string> = {};
  if (token) headers.Authorization = `Bearer ${token}`;
  const response = await monitoredFetch(`${base}${path}`, { headers });
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

export const challansService = {
  listViolations(): Promise<ViolationMaster[]> {
    return getApiData<ViolationMaster[]>("/v1/challans/violations");
  },

  searchVehicle(registrationNumber: string): Promise<VehicleChallanSearchData> {
    const encoded = encodeURIComponent(registrationNumber.trim());
    return getApiData<VehicleChallanSearchData>(`/v1/challans/search?registration_number=${encoded}`);
  },

  listChallans(filters: ChallansFilters = {}): Promise<ChallansListData> {
    return getApiData<ChallansListData>(`/v1/challans${toQueryString(filters)}`);
  },

  getAnalytics(): Promise<ChallanAnalyticsData> {
    return getApiData<ChallanAnalyticsData>("/v1/challans/analytics");
  },

  createChallan(payload: CreateChallanPayload): Promise<ChallanMutationData> {
    return postApiData<ChallanMutationData>("/v1/challans", payload);
  },

  cancelChallan(challanId: string): Promise<ChallanMutationData> {
    return postApiData<ChallanMutationData>(`/v1/challans/${challanId}/cancel`, {});
  },

  markPaid(challanId: string): Promise<ChallanMutationData> {
    return postApiData<ChallanMutationData>(`/v1/challans/${challanId}/mark-paid`, {});
  },

  deleteChallan(challanId: string): Promise<void> {
    const base = env.apiBaseUrl.replace(/\/$/, "");
    const token = getAccessToken();
    const headers: Record<string, string> = {};
    if (token) headers.Authorization = `Bearer ${token}`;
    return monitoredFetch(`${base}/v1/challans/${challanId}`, { method: "DELETE", headers }).then((response) => {
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
    });
  },

  downloadPdf(challanId: string, challanNumber: string): Promise<void> {
    return downloadBinary(`/v1/challans/${challanId}/download`, `${challanNumber}.pdf`);
  },
};
