export type RiskLevel = "low" | "medium" | "high" | "critical";

export interface ScanHistoryItem {
  scan_id: string;
  plate_text: string;
  vehicle_id: string | null;
  officer_id: string;
  officer_name: string;
  risk_score: number;
  risk_level: RiskLevel;
  location_label: string | null;
  scanned_at: string;
  completed_at: string;
}

export interface Pagination {
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
}

export interface ScanHistoryList {
  items: ScanHistoryItem[];
  pagination: Pagination;
}

export interface ScanHistoryFilters {
  plate?: string;
  officer_id?: string;
  risk_level?: RiskLevel;
  from?: string;
  to?: string;
  page?: number;
  page_size?: number;
}

export interface SaveCompletedScanRequest {
  plate: string;
  risk_score: number;
  risk_level: RiskLevel;
  vehicle_id?: string;
  location_label?: string;
}

export interface SaveCompletedScanResult {
  scan_id: string;
  plate_text: string;
  scanned_at: string;
  completed_at: string;
}
