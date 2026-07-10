/** Dashboard API types. */

export interface DashboardSummary {
  total_scans: number;
  verified_vehicles: number;
  suspicious_vehicles: number;
  pending_verification: number;
  last_updated_at: string;
}

export interface RecentActivityItem {
  id: string;
  plate_text: string;
  activity_type: string;
  description: string;
  status: string;
  occurred_at: string;
}

export interface RecentActivity {
  items: RecentActivityItem[];
}
