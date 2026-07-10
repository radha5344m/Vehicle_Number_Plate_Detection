import { Activity } from "lucide-react";
import { ExecutiveCommandCenter } from "@/components/features/dashboard/ExecutiveCommandCenter";
import { Alert } from "@/components/ui/Alert";
import { LoadingState } from "@/components/ui/LoadingState";
import { PageHeader } from "@/components/ui/PageHeader";
import { useExecutiveDashboard } from "@/hooks/dashboard/useExecutiveDashboard";
import { AppLayout } from "@/layouts/AppLayout";
import { DEFAULT_EXECUTIVE_DASHBOARD_FILTERS } from "@/lib/executiveDashboardFilters";

export function DashboardPage() {
  const { data, loading, error, filters, setFilters, refresh, exportDashboard } = useExecutiveDashboard();

  return (
    <AppLayout>
      <div className="space-y-8">
        <PageHeader
          badge="Executive Intelligence"
          title="Executive Command Center"
          description="Live command-center analytics, scoped automatically to your role and operational jurisdiction."
        />

        {loading && <LoadingState label="Loading dashboard metrics…" fullHeight />}

        {error && !loading && (
          <Alert variant="warning" title="Dashboard Unavailable">
            {error} — ensure the backend is running on port 8080.
          </Alert>
        )}

        {data && !loading && (
          <ExecutiveCommandCenter
            data={data}
            filters={filters}
            onApplyFilters={setFilters}
            onResetFilters={() => setFilters({ ...DEFAULT_EXECUTIVE_DASHBOARD_FILTERS })}
            onRefresh={refresh}
            onExport={exportDashboard}
            showFilters={false}
          />
        )}

        {data && (
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <Activity className="h-3.5 w-3.5 text-secondary" aria-hidden />
            {data.connection_status.status} · last updated{" "}
            {new Date(data.connection_status.last_updated_at).toLocaleString()} · auto refresh{" "}
            {data.connection_status.auto_refresh_seconds}s
          </div>
        )}
      </div>
    </AppLayout>
  );
}
