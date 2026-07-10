import { AlertTriangle, CheckCircle2, Gauge, ShieldAlert, Sparkles, FileSearch } from "lucide-react";

import { Card } from "@/components/ui/Card";
import type { InvestigationSummary } from "@/types/api/investigationReports";

function Metric({ label, value, suffix }: { label: string; value: string; suffix?: string }) {
  return (
    <div>
      <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-1 text-2xl font-bold text-slate-900">
        {value}
        {suffix ? <span className="ml-1 text-sm font-medium text-slate-400">{suffix}</span> : null}
      </p>
    </div>
  );
}

function asText(value: string | null | undefined): string {
  return value && value.trim() ? value : "�";
}

interface Props {
  summary: InvestigationSummary;
}

export function InvestigationReportsSummaryCards({ summary }: Props) {
  const avgRisk = summary.average_risk_score != null ? `${Math.round(summary.average_risk_score * 100)}` : "�";
  const avgConfidence =
    summary.average_ai_confidence != null
      ? `${Math.round(summary.average_ai_confidence * 100)}`
      : "�";
  const avgTime =
    summary.average_investigation_time_minutes != null
      ? summary.average_investigation_time_minutes.toFixed(1)
      : "�";

  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      <Card title="Investigation Summary" description={summary.investigation_summary} icon={<FileSearch className="h-4 w-4" />} accent>
        <Metric label="Total Investigations" value={String(summary.total_investigations)} />
      </Card>
      <Card title="Verified Vehicles" icon={<CheckCircle2 className="h-4 w-4" />}>
        <Metric label="Verified" value={String(summary.verified_vehicles)} />
      </Card>
      <Card title="Suspicious Vehicles" icon={<AlertTriangle className="h-4 w-4" />}>
        <Metric label="Flagged" value={String(summary.suspicious_vehicles)} />
      </Card>
      <Card title="High Risk Vehicles" icon={<ShieldAlert className="h-4 w-4" />}>
        <Metric label="High Risk" value={String(summary.high_risk_vehicles)} />
      </Card>
      <Card title="Average Risk Score" icon={<Gauge className="h-4 w-4" />}>
        <Metric label="Risk Score" value={avgRisk} suffix="/100" />
      </Card>
      <Card title="Average AI Confidence" icon={<Sparkles className="h-4 w-4" />}>
        <Metric label="AI Confidence" value={avgConfidence} suffix="%" />
      </Card>
      <Card title="Average Investigation Time" icon={<Gauge className="h-4 w-4" />}>
        <Metric label="Avg Duration" value={avgTime} suffix="min" />
      </Card>
      <Card title="Top Vehicle Type" icon={<FileSearch className="h-4 w-4" />}>
        <Metric label="Vehicle Type" value={asText(summary.top_vehicle_type)} />
      </Card>
      <Card title="Top Vehicle Brand" icon={<FileSearch className="h-4 w-4" />}>
        <Metric label="Vehicle Brand" value={asText(summary.top_vehicle_brand)} />
      </Card>
      <Card title="Most Active Officer" icon={<CheckCircle2 className="h-4 w-4" />}>
        <Metric label="Officer" value={asText(summary.most_active_officer)} />
      </Card>
      <Card title="Most Active Station" icon={<ShieldAlert className="h-4 w-4" />}>
        <Metric label="Station" value={asText(summary.most_active_station)} />
      </Card>
    </div>
  );
}
