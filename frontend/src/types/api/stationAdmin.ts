export interface StationAdminDashboardSummary {
  todays_investigations: number;
  weekly_investigations: number;
  monthly_investigations: number;
  high_risk_vehicles: number;
  verified_vehicles: number;
  pending_investigations: number;
  average_ai_confidence: number | null;
  average_risk_score: number | null;
}

export interface StationAdminRecentInvestigation {
  investigation_id: string;
  registration_number: string;
  officer_name: string;
  risk_level: string;
  verification_status: string | null;
  scanned_at: string;
}

export interface StationAdminRecentOfficerActivity {
  activity_id: string;
  officer_name: string;
  description: string;
  status: string;
  occurred_at: string;
}

export interface StationAdminHighRiskVehicle {
  registration_number: string;
  risk_score: number;
  reason: string;
  officer_name: string;
  occurred_at: string;
}

export interface StationAdminDashboardData {
  summary: StationAdminDashboardSummary;
  recent_investigations: StationAdminRecentInvestigation[];
  recent_officer_activity: StationAdminRecentOfficerActivity[];
  high_risk_vehicles: StationAdminHighRiskVehicle[];
}

export interface StationAdminOfficerItem {
  officer_id: string;
  employee_id: string;
  badge_number: string;
  officer_name: string;
  rank: string;
  phone_number: string | null;
  status: string;
  investigations: number;
  last_login_at: string | null;
  username: string;
  email: string;
  created_at: string;
}

export interface StationAdminOfficerList {
  items: StationAdminOfficerItem[];
  pagination: { page: number; page_size: number; total_items: number; total_pages: number };
}

export interface CreateOfficerRequest {
  employee_id: string;
  first_name: string;
  last_name: string;
  username: string;
  email: string;
  phone_number?: string;
  badge_number: string;
  rank: string;
  status: string;
}

export interface OfficerMutationResult {
  officer: StationAdminOfficerItem;
  temporary_password?: string | null;
  password_change_required?: boolean;
}

export interface UpdateStationDetailsRequest {
  address: string;
  phone_number?: string;
  email?: string;
}

export interface UpdateOfficerRequest {
  first_name: string;
  last_name: string;
  email: string;
  phone_number?: string;
  rank: string;
  status: string;
}

export interface StationAdminAnalyticsData {
  daily_labels: string[];
  daily_investigations: number[];
  weekly_labels: string[];
  weekly_trend: number[];
  monthly_labels: string[];
  monthly_trend: number[];
  risk_distribution_labels: string[];
  risk_distribution_values: number[];
  vehicle_type_labels: string[];
  vehicle_type_values: number[];
  vehicle_brand_labels: string[];
  vehicle_brand_values: number[];
  officer_performance_labels: string[];
  officer_performance_values: number[];
  average_investigation_time_minutes: number | null;
  average_ai_confidence: number | null;
  average_risk_score: number | null;
}

export interface StationAdminNotification {
  notification_id: string;
  title: string;
  message: string;
  category: string;
  occurred_at: string;
}

export interface StationAdminNotificationsData {
  items: StationAdminNotification[];
}

export interface StationAdminProfileData {
  station_id: string;
  station_name: string;
  station_code: string;
  address: string;
  phone_number: string | null;
  email: string | null;
  district: string;
  state: string;
  station_type: string;
  admin_name: string;
  admin_rank: string;
  officer_id: string;
  employee_id: string;
  role: string;
  account_email: string;
  account_phone: string | null;
  created_at: string;
  last_login_at: string | null;
}

export interface ActionMessage {
  message: string;
}
