import { Filter, RotateCcw } from "lucide-react";
import { useEffect, useState } from "react";
import { ChartCard } from "@/components/features/analytics/ChartCard";
import {
  DailyScansChart,
  OfficerActivityChart,
  RiskDistributionChart,
  SuspiciousVehiclesChart,
  VehicleTypesChart,
} from "@/components/features/analytics/AnalyticsCharts";
import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { LoadingState } from "@/components/ui/LoadingState";
import { PageHeader } from "@/components/ui/PageHeader";
import { useAnalyticsOverview } from "@/hooks/analytics/useAnalyticsOverview";
import { AppLayout } from "@/layouts/AppLayout";
import {
  buildDateRangeFilters,
  dateRangeToDraft,
  validateDateRangeDraft,
  type DateRangeDraft,
} from "@/lib/dateRangeFilters";
import { hasRole } from "@/lib/rbac";
import { StationAnalyticsPage } from "@/pages/stationAdmin/StationAnalyticsPage";

export function AnalyticsPage() {
  if (hasRole("STATION_ADMIN")) {
    return <StationAnalyticsPage />;
  }
  const { data, loading, error, filters, setFilters } = useAnalyticsOverview();
  const [draft, setDraft] = useState<DateRangeDraft>(() => dateRangeToDraft(filters));
  const [dateError, setDateError] = useState<string | null>(null);

  useEffect(() => {
    setDraft(dateRangeToDraft(filters));
    setDateError(null);
  }, [filters]);

  function handleReset() {
    setDateError(null);
    setFilters({});
  }

  return (
    <AppLayout>
      <div className="space-y-6">
        <PageHeader
          badge="Intelligence"
          title="Analytics"
          description="Insights from stored scan history — aggregated metrics, no live AI processing."
        />

        <Card title="Date Range Filter" icon={<Filter className="h-4 w-4" />}>
          <form
            className="grid gap-4 md:grid-cols-3"
            onSubmit={(event) => {
              event.preventDefault();
              const rangeError = validateDateRangeDraft(draft.from, draft.to);
              if (rangeError) {
                setDateError(rangeError);
                return;
              }
              setDateError(null);
              setFilters(buildDateRangeFilters(draft));
            }}
          >
            <Input
              type="date"
              name="from"
              label="From Date"
              value={draft.from}
              onChange={(event) => {
                setDraft((current) => ({ ...current, from: event.target.value }));
                setDateError(null);
              }}
            />
            <Input
              type="date"
              name="to"
              label="To Date"
              value={draft.to}
              onChange={(event) => {
                setDraft((current) => ({ ...current, to: event.target.value }));
                setDateError(null);
              }}
            />
            <div className="flex items-end gap-2">
              <Button type="submit" className="w-full md:w-auto">
                Apply Range
              </Button>
              <Button
                type="button"
                variant="secondary"
                icon={<RotateCcw className="h-4 w-4" />}
                onClick={handleReset}
              >
                Reset Filters
              </Button>
            </div>
            {dateError && <p className="text-sm text-red-600 md:col-span-3">{dateError}</p>}
          </form>
        </Card>

        {loading && <LoadingState label="Loading analytics…" fullHeight />}

        {error && !loading && (
          <Alert variant="warning" title="Analytics Unavailable">
            {error} — ensure the backend is running and you are logged in.
          </Alert>
        )}

        {data && !loading && (
          <div className="animate-fade-in space-y-6">
            <p className="text-sm text-slate-500">
              {data.total_scans} scans analyzed · Updated{" "}
              {new Date(data.generated_at).toLocaleString()}
              {(filters.from || filters.to) && " · filtered range applied"}
            </p>

            <div className="grid gap-6 lg:grid-cols-2">
              <ChartCard title="Daily Scans" description="Completed scans per day">
                <DailyScansChart series={data.daily_scans} />
              </ChartCard>

              <ChartCard title="Risk Distribution" description="Scans grouped by risk level">
                <RiskDistributionChart series={data.risk_distribution} />
              </ChartCard>

              <ChartCard title="Vehicle Types" description="Distribution from linked registry records">
                <VehicleTypesChart series={data.vehicle_types} />
              </ChartCard>

              <ChartCard title="Suspicious Vehicles" description="Plates with high or critical risk">
                <SuspiciousVehiclesChart items={data.suspicious_vehicles} />
              </ChartCard>

              <ChartCard title="Officer Activity" description="Scan counts by officer">
                <OfficerActivityChart series={data.officer_activity} />
              </ChartCard>
            </div>
          </div>
        )}
      </div>
    </AppLayout>
  );
}
