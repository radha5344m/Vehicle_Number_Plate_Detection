import { Filter, RotateCcw } from "lucide-react";
import { useEffect, useState } from "react";

import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { LoadingState } from "@/components/ui/LoadingState";
import { PageHeader } from "@/components/ui/PageHeader";
import { useStationAnalytics } from "@/hooks/stationAdmin/useStationAdmin";
import { AppLayout } from "@/layouts/AppLayout";
import {
  buildDateRangeFilters,
  dateRangeToDraft,
  validateDateRangeDraft,
  type DateRangeDraft,
} from "@/lib/dateRangeFilters";

export function StationAnalyticsPage() {
  const { data, loading, error, filters, setFilters } = useStationAnalytics();
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
          badge="Station Analytics"
          title="Analytics"
          description="Daily, weekly, monthly, risk, vehicle, and officer performance analytics for your station."
        />

        <Card title="Date Range" icon={<Filter className="h-4 w-4" />}>
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
              label="From"
              value={draft.from}
              onChange={(event) => {
                setDraft((current) => ({ ...current, from: event.target.value }));
                setDateError(null);
              }}
            />
            <Input
              type="date"
              name="to"
              label="To"
              value={draft.to}
              onChange={(event) => {
                setDraft((current) => ({ ...current, to: event.target.value }));
                setDateError(null);
              }}
            />
            <div className="flex items-end gap-2">
              <Button type="submit">Apply</Button>
              <Button type="button" variant="secondary" icon={<RotateCcw className="h-4 w-4" />} onClick={handleReset}>
                Reset Filters
              </Button>
            </div>
            {dateError && <p className="text-sm text-red-600 md:col-span-3">{dateError}</p>}
          </form>
        </Card>

        {loading && <LoadingState label="Loading analytics..." fullHeight />}
        {error && !loading && (
          <Alert variant="warning" title="Analytics Unavailable">
            {error}
          </Alert>
        )}
        {data && !loading && (
          <div className="grid gap-6 lg:grid-cols-2">
            {[
              ["Average Investigation Time", data.average_investigation_time_minutes?.toFixed(1) ?? "-"],
              [
                "Average AI Confidence",
                data.average_ai_confidence != null ? `${Math.round(data.average_ai_confidence * 100)}%` : "-",
              ],
              [
                "Average Risk Score",
                data.average_risk_score != null ? `${Math.round(data.average_risk_score * 100)}%` : "-",
              ],
              ["Daily Investigations", data.daily_investigations.reduce((sum, value) => sum + value, 0)],
            ].map(([label, value]) => (
              <Card key={label}>
                <p className="text-sm text-slate-500">{label}</p>
                <p className="mt-2 text-2xl font-bold text-slate-900">{value}</p>
              </Card>
            ))}
            <Card title="Weekly Trend" className="lg:col-span-2">
              <ul className="grid gap-3 md:grid-cols-3">
                {data.weekly_labels.map((label, index) => (
                  <li key={label} className="rounded-lg border border-slate-100 px-3 py-2 text-sm">
                    <p className="font-medium text-slate-900">{label}</p>
                    <p className="text-slate-500">{data.weekly_trend[index]} investigations</p>
                  </li>
                ))}
              </ul>
            </Card>
            <Card title="Monthly Trend" className="lg:col-span-2">
              <ul className="grid gap-3 md:grid-cols-3">
                {data.monthly_labels.map((label, index) => (
                  <li key={label} className="rounded-lg border border-slate-100 px-3 py-2 text-sm">
                    <p className="font-medium text-slate-900">{label}</p>
                    <p className="text-slate-500">{data.monthly_trend[index]} investigations</p>
                  </li>
                ))}
              </ul>
            </Card>
            <Card title="Risk Distribution">
              <ul className="space-y-2">
                {data.risk_distribution_labels.map((label, index) => (
                  <li key={label} className="flex justify-between text-sm">
                    <span>{label}</span>
                    <span>{data.risk_distribution_values[index]}</span>
                  </li>
                ))}
              </ul>
            </Card>
            <Card title="Vehicle Type Distribution">
              <ul className="space-y-2">
                {data.vehicle_type_labels.map((label, index) => (
                  <li key={label} className="flex justify-between text-sm">
                    <span>{label}</span>
                    <span>{data.vehicle_type_values[index]}</span>
                  </li>
                ))}
              </ul>
            </Card>
            <Card title="Vehicle Brand Distribution">
              <ul className="space-y-2">
                {data.vehicle_brand_labels.map((label, index) => (
                  <li key={label} className="flex justify-between text-sm">
                    <span>{label}</span>
                    <span>{data.vehicle_brand_values[index]}</span>
                  </li>
                ))}
              </ul>
            </Card>
            <Card title="Officer Performance">
              <ul className="space-y-2">
                {data.officer_performance_labels.map((label, index) => (
                  <li key={label} className="flex justify-between text-sm">
                    <span>{label}</span>
                    <span>{data.officer_performance_values[index]}</span>
                  </li>
                ))}
              </ul>
            </Card>
          </div>
        )}
      </div>
    </AppLayout>
  );
}
