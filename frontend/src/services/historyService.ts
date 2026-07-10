import { getApiData, postApiData } from "@/services/api/httpClient";
import type {
  SaveCompletedScanRequest,
  SaveCompletedScanResult,
  ScanHistoryFilters,
  ScanHistoryList,
} from "@/types/api/history";

function toQueryString(filters: ScanHistoryFilters): string {
  const params = new URLSearchParams();
  if (filters.plate) params.set("plate", filters.plate);
  if (filters.officer_id) params.set("officer_id", filters.officer_id);
  if (filters.risk_level) params.set("risk_level", filters.risk_level);
  if (filters.from) params.set("from", filters.from);
  if (filters.to) params.set("to", filters.to);
  if (filters.page) params.set("page", String(filters.page));
  if (filters.page_size) params.set("page_size", String(filters.page_size));
  const query = params.toString();
  return query ? `?${query}` : "";
}

export const historyService = {
  getScanHistory(filters: ScanHistoryFilters = {}): Promise<ScanHistoryList> {
    return getApiData<ScanHistoryList>(`/v1/history/scans${toQueryString(filters)}`);
  },

  saveCompletedScan(body: SaveCompletedScanRequest): Promise<SaveCompletedScanResult> {
    return postApiData<SaveCompletedScanResult>("/v1/history/scans", body);
  },
};
