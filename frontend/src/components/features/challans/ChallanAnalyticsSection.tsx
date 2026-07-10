import {
  AlertTriangle,
  Banknote,
  CheckCircle2,
  Clock3,
  FileWarning,
  IndianRupee,
  TrendingUp,
  Users,
} from "lucide-react";

import { Card } from "@/components/ui/Card";
import { LoadingState } from "@/components/ui/LoadingState";
import { formatChallanInr, formatViolationLabel } from "@/components/features/challans/ChallanStatusBadge";
import type { ChallanAnalyticsData } from "@/types/api/challans";

interface Props {
  data: ChallanAnalyticsData | null;
  loading: boolean;
}

function MetricCard({
  label,
  value,
  icon,
  accent,
}: {
  label: string;
  value: string;
  icon: React.ReactNode;
  accent?: "green" | "yellow" | "red" | "blue";
}) {
  const ring =
    accent === "green"
      ? "ring-green-100"
      : accent === "yellow"
        ? "ring-amber-100"
        : accent === "red"
          ? "ring-red-100"
          : "ring-blue-100";
  return (
    <div className={`rounded-2xl border border-slate-200 bg-white p-4 shadow-soft ring-1 ${ring}`}>
      <div className="mb-2 flex items-center justify-between">
        <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{label}</p>
        <span className="text-brand">{icon}</span>
      </div>
      <p className="text-2xl font-bold text-slate-900">{value}</p>
    </div>
  );
}

export function ChallanAnalyticsSection({ data, loading }: Props) {
  if (loading) return <LoadingState label="Loading challan analytics…" />;
  if (!data) return null;

  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Total Challans" value={String(data.total_challans)} icon={<FileWarning className="h-4 w-4" />} />
        <MetricCard label="Today's Challans" value={String(data.todays_challans)} icon={<Clock3 className="h-4 w-4" />} accent="blue" />
        <MetricCard label="Pending Challans" value={String(data.pending_challans)} icon={<AlertTriangle className="h-4 w-4" />} accent="yellow" />
        <MetricCard label="Paid Challans" value={String(data.paid_challans)} icon={<CheckCircle2 className="h-4 w-4" />} accent="green" />
        <MetricCard label="Collected Fine" value={formatChallanInr(data.collected_fine_inr)} icon={<IndianRupee className="h-4 w-4" />} accent="green" />
        <MetricCard label="Outstanding Fine" value={formatChallanInr(data.outstanding_fine_inr)} icon={<Banknote className="h-4 w-4" />} accent="red" />
        <MetricCard
          label="Most Common Violation"
          value={data.most_common_violation ? formatViolationLabel(data.most_common_violation) : "—"}
          icon={<TrendingUp className="h-4 w-4" />}
        />
        <MetricCard label="Top Issuing Officer" value={data.top_issuing_officer ?? "—"} icon={<Users className="h-4 w-4" />} />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card title="Violation Distribution" description="Issued challans by violation type">
          {data.violation_distribution.length === 0 ? (
            <p className="text-sm text-slate-500">No challan data yet.</p>
          ) : (
            <ul className="space-y-2">
              {data.violation_distribution.map((item) => (
                <li key={item.label} className="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-2 text-sm">
                  <span className="font-medium text-slate-700">{formatViolationLabel(item.label)}</span>
                  <span className="font-semibold text-slate-900">{item.value}</span>
                </li>
              ))}
            </ul>
          )}
        </Card>

        <Card title="Monthly Fine Collection" description="Collected fines and issued challans">
          {data.monthly_fine_collection.length === 0 ? (
            <p className="text-sm text-slate-500">No collection data yet.</p>
          ) : (
            <ul className="space-y-2">
              {data.monthly_fine_collection.map((item) => (
                <li key={item.month} className="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-2 text-sm">
                  <span className="font-medium text-slate-700">{item.month}</span>
                  <span className="text-right">
                    <span className="block font-semibold text-slate-900">{formatChallanInr(item.collected_fine_inr)}</span>
                    <span className="text-xs text-slate-500">{item.issued_count} issued</span>
                  </span>
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>

      {data.top_station ? (
        <p className="text-sm text-slate-500">
          Top station: <span className="font-semibold text-slate-800">{data.top_station}</span>
        </p>
      ) : null}
    </div>
  );
}
