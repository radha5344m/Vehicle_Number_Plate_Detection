import { getApiData } from "@/services/api/httpClient";
import type { AnalyticsFilters, AnalyticsOverview } from "@/types/api/analytics";

function toQueryString(filters: AnalyticsFilters): string {
  const params = new URLSearchParams();
  if (filters.from) params.set("from", filters.from);
  if (filters.to) params.set("to", filters.to);
  const query = params.toString();
  return query ? `?${query}` : "";
}

export const analyticsService = {
  getOverview(filters: AnalyticsFilters = {}): Promise<AnalyticsOverview> {
    return getApiData<AnalyticsOverview>(`/v1/analytics/overview${toQueryString(filters)}`);
  },
};
