import { useEffect, useState } from "react";
import { dashboardService } from "@/services/dashboardService";
import type { RecentActivityItem } from "@/types/api/dashboard";

interface UseRecentActivityResult {
  items: RecentActivityItem[];
  loading: boolean;
  error: string | null;
}

export function useRecentActivity(limit = 8): UseRecentActivityResult {
  const [items, setItems] = useState<RecentActivityItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);

    dashboardService
      .getRecentActivity(limit)
      .then((data) => {
        if (!cancelled) setItems(data.items);
      })
      .catch(() => {
        if (!cancelled) setError("Failed to load recent activity");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [limit]);

  return { items, loading, error };
}
