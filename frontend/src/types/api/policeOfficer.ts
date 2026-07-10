import type { InvestigationReportsData, InvestigationReportsFilters } from "@/types/api/investigationReports";

export interface PoliceOfficerDashboardSummary {
  todays_verifications: number;
  weekly_verifications: number;
  monthly_verifications: number;
  high_risk_vehicles_found: number;
  average_ai_confidence: number | null;
  average_risk_score: number | null;
}

export interface PoliceOfficerRecentInvestigation {
  investigation_id: string;
  registration_number: string;
  vehicle_type: string | null;
  risk_level: string;
  verification_status: string | null;
  scanned_at: string;
  report_download_url: string | null;
}

export interface PoliceOfficerRecentActivity {
  activity_id: string;
  description: string;
  status: string;
  occurred_at: string;
}

export interface PoliceOfficerDashboardData {
  summary: PoliceOfficerDashboardSummary;
  recent_investigations: PoliceOfficerRecentInvestigation[];
  recent_activity: PoliceOfficerRecentActivity[];
}

export interface PoliceOfficerNotification {
  notification_id: string;
  title: string;
  message: string;
  category: string;
  occurred_at: string;
}

export interface PoliceOfficerNotificationsData {
  items: PoliceOfficerNotification[];
}

export interface PoliceOfficerProfileData {
  officer_id: string;
  employee_id: string;
  officer_name: string;
  badge_number: string;
  rank: string;
  station_name: string;
  station_code: string;
  phone_number: string | null;
  email: string;
  username: string;
  role: string;
  created_at: string;
  last_login_at: string | null;
}

export interface ActionMessage {
  message: string;
}

export type PoliceOfficerReportsFilters = InvestigationReportsFilters;
export type PoliceOfficerReportsData = InvestigationReportsData;
