export type RiskLevel = "low" | "medium" | "high" | "critical";
export type VerificationStatus = "found" | "not_found" | "pending" | "unknown";
export type SortBy =
  | "scanned_at"
  | "risk_score"
  | "ai_confidence"
  | "officer_name"
  | "registration_number"
  | "police_station";

export interface InvestigationReportsFilters {
  from?: string;
  to?: string;
  search?: string;
  officer?: string;
  police_station?: string;
  district?: string;
  risk_level?: RiskLevel;
  vehicle_type?: string;
  vehicle_brand?: string;
  registration_number?: string;
  owner_name?: string;
  verification_status?: VerificationStatus;
  investigation_status?: "completed" | "pending";
  ai_confidence_min?: number;
  ai_confidence_max?: number;
  page?: number;
  page_size?: number;
  sort_by?: SortBy;
  sort_desc?: boolean;
}

export interface DistributionItem {
  label: string;
  value: number;
}

export interface OfficerPerformanceItem {
  officer_id: string;
  officer_name: string;
  investigations: number;
  verified_vehicles: number;
  high_risk_vehicles: number;
  average_risk_score: number;
  average_ai_confidence: number | null;
}

export interface DailyInvestigationTrendPoint {
  date: string;
  investigations: number;
}

export interface PeriodInvestigationTrendPoint {
  period: string;
  investigations: number;
}

export interface InvestigationSummary {
  investigation_summary: string;
  total_investigations: number;
  verified_vehicles: number;
  suspicious_vehicles: number;
  high_risk_vehicles: number;
  average_risk_score: number | null;
  average_ai_confidence: number | null;
  average_investigation_time_minutes: number | null;
  top_vehicle_type: string | null;
  top_vehicle_brand: string | null;
  most_active_officer: string | null;
  most_active_station: string | null;
}

export interface InvestigationReportListItem {
  scanned_at: string;
  completed_at: string;
  investigation_id: string;
  registration_number: string;
  owner: string | null;
  vehicle: string | null;
  brand: string | null;
  model: string | null;
  officer_id: string;
  officer_name: string;
  station_name: string | null;
  district: string | null;
  police_station: string | null;
  risk_score: number;
  risk_level: RiskLevel;
  investigation_status: string;
  verification_status: string | null;
  ai_confidence: number | null;
  report_id: string | null;
  report_download_url: string | null;
  vehicle_type?: string | null;
  verification_message?: string | null;
}

export interface StationPerformanceItem {
  station_name: string;
  investigations: number;
  verified_vehicles: number;
  high_risk_vehicles: number;
  average_risk_score: number;
  average_ai_confidence: number | null;
}

export interface InvestigationReportsPagination {
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
}

export interface InvestigationReportsData {
  summary: InvestigationSummary;
  risk_distribution: DistributionItem[];
  vehicle_type_distribution: DistributionItem[];
  brand_distribution: DistributionItem[];
  officer_performance: OfficerPerformanceItem[];
  station_performance: StationPerformanceItem[];
  verification_status_distribution: DistributionItem[];
  daily_investigation_trend: DailyInvestigationTrendPoint[];
  weekly_investigation_trend: PeriodInvestigationTrendPoint[];
  monthly_investigation_trend: PeriodInvestigationTrendPoint[];
  items: InvestigationReportListItem[];
  pagination: InvestigationReportsPagination;
  generated_at: string;
}
