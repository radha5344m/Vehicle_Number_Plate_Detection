export interface ExecutiveDashboardFilters {
  from?: string;
  to?: string;
  district?: string;
  station?: string;
  officer?: string;
  vehicle_type?: string;
  risk_level?: string;
  brand?: string;
}

export interface MetricCard {
  label: string;
  value: number;
  display_value: string;
}

export interface ChartPoint {
  label: string;
  value: number;
}

export interface ActivityFeedItem {
  id: string;
  title: string;
  detail: string;
  category: string;
  occurred_at: string;
}

export interface LeaderboardItem {
  name: string;
  metric: string;
  value: number;
  secondary_value?: string | null;
}

export interface ExecutiveInsight {
  title: string;
  detail: string;
}

export interface ExecutiveConnectionStatus {
  status: string;
  last_updated_at: string;
  auto_refresh_seconds: number;
}

export interface ExecutiveDashboardData {
  scope_label: string;
  kpis: MetricCard[];
  daily_trend: ChartPoint[];
  weekly_trend: ChartPoint[];
  monthly_trend: ChartPoint[];
  hourly_activity: ChartPoint[];
  investigation_status_distribution: ChartPoint[];
  risk_distribution: ChartPoint[];
  risk_trend: ChartPoint[];
  top_high_risk_registrations: ChartPoint[];
  frequent_suspicious_vehicles: ChartPoint[];
  vehicle_type_distribution: ChartPoint[];
  vehicle_brand_distribution: ChartPoint[];
  vehicle_color_distribution: ChartPoint[];
  registration_state_distribution: ChartPoint[];
  common_vehicle_models: ChartPoint[];
  top_performing_officers: LeaderboardItem[];
  most_active_officers: LeaderboardItem[];
  officer_leaderboard: LeaderboardItem[];
  top_performing_stations: LeaderboardItem[];
  recent_investigations: ActivityFeedItem[];
  recent_high_risk_alerts: ActivityFeedItem[];
  recent_officer_activity: ActivityFeedItem[];
  recent_reports_generated: ActivityFeedItem[];
  ai_metrics: MetricCard[];
  insights: ExecutiveInsight[];
  connection_status: ExecutiveConnectionStatus;
}
