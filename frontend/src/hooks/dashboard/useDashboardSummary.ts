import { useEffect, useState } from "react";
import { dashboardService } from "@/services/dashboardService";
import type { DashboardSummary } from "@/types/api/dashboard";

interface UseDashboardSummaryResult {
  summary: DashboardSummary | null;
  loading: boolean;
  error: string | null;
}

export function useDashboardSummary(): UseDashboardSummaryResult {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);

    dashboardService
      .getSummary()
      .then((data) => {
        if (!cancelled) setSummary(data);
      })
      .catch(() => {
        if (!cancelled) setError("Failed to load dashboard summary");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  return { summary, loading, error };
}
