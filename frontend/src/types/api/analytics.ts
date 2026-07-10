export interface ChartSeries {
  labels: string[];
  values: number[];
}

export interface SuspiciousVehicleItem {
  plate_text: string;
  scan_count: number;
  max_risk_score: number;
  risk_level: string;
}

export interface AnalyticsOverview {
  daily_scans: ChartSeries;
  risk_distribution: ChartSeries;
  vehicle_types: ChartSeries;
  suspicious_vehicles: SuspiciousVehicleItem[];
  officer_activity: ChartSeries;
  total_scans: number;
  generated_at: string;
}

export interface AnalyticsFilters {
  from?: string;
  to?: string;
}
