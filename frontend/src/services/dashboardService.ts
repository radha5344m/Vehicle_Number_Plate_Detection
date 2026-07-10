import { getApiData } from "@/services/api/httpClient";
import type { DashboardSummary, RecentActivity } from "@/types/api/dashboard";

export const dashboardService = {
  getSummary(): Promise<DashboardSummary> {
    return getApiData<DashboardSummary>("/v1/dashboard/summary");
  },

  getRecentActivity(limit = 10): Promise<RecentActivity> {
    return getApiData<RecentActivity>(`/v1/dashboard/recent-activity?limit=${limit}`);
  },
};
