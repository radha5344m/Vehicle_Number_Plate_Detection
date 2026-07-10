import { Card } from "@/components/ui/Card";
import type {
  DailyInvestigationTrendPoint,
  DistributionItem,
  OfficerPerformanceItem,
  PeriodInvestigationTrendPoint,
  StationPerformanceItem,
} from "@/types/api/investigationReports";

function DistributionList({ items }: { items: DistributionItem[] }) {
  const max = Math.max(...items.map((item) => item.value), 1);
  if (items.length === 0) {
    return <p className="text-sm text-slate-500">No data available.</p>;
  }
  return (
    <div className="space-y-3">
      {items.map((item) => (
        <div key={item.label}>
          <div className="mb-1 flex items-center justify-between text-sm">
            <span className="font-medium text-slate-700">{item.label}</span>
            <span className="font-mono text-slate-500">{item.value}</span>
          </div>
          <div className="h-2 overflow-hidden rounded-full bg-slate-200">
            <div
              className="h-full rounded-full bg-brand"
              style={{ width: `${Math.max((item.value / max) * 100, 4)}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}

function TrendBars({ items }: { items: DailyInvestigationTrendPoint[] }) {
  const max = Math.max(...items.map((item) => item.investigations), 1);
  if (items.length === 0) {
    return <p className="text-sm text-slate-500">No data available.</p>;
  }
  return (
    <div className="flex h-48 items-end gap-2">
      {items.slice(-14).map((item) => (
        <div key={item.date} className="flex flex-1 flex-col items-center gap-2">
          <div className="w-full rounded-t bg-blue-600" style={{ height: `${(item.investigations / max) * 100}%` }} />
          <span className="text-[10px] text-slate-500">{item.date.slice(5)}</span>
        </div>
      ))}
    </div>
  );
}

function PeriodTrendBars({
  items,
  labelFormatter,
}: {
  items: PeriodInvestigationTrendPoint[];
  labelFormatter?: (value: string) => string;
}) {
  const max = Math.max(...items.map((item) => item.investigations), 1);
  if (items.length === 0) {
    return <p className="text-sm text-slate-500">No data available.</p>;
  }
  return (
    <div className="flex h-48 items-end gap-2">
      {items.slice(-12).map((item) => (
        <div key={item.period} className="flex flex-1 flex-col items-center gap-2">
          <div className="w-full rounded-t bg-blue-600" style={{ height: `${(item.investigations / max) * 100}%` }} />
          <span className="text-[10px] text-slate-500">
            {labelFormatter ? labelFormatter(item.period) : item.period}
          </span>
        </div>
      ))}
    </div>
  );
}

function OfficerTable({ items }: { items: OfficerPerformanceItem[] }) {
  if (items.length === 0) {
    return <p className="text-sm text-slate-500">No officer data available.</p>;
  }
  return (
    <div className="table-scroll overflow-x-auto">
      <table className="min-w-full text-sm">
        <thead className="text-left text-xs uppercase tracking-wide text-slate-500">
          <tr>
            <th className="py-2 pr-3">Officer</th>
            <th className="py-2 pr-3">Investigations</th>
            <th className="py-2 pr-3">Verified</th>
            <th className="py-2 pr-3">High Risk</th>
            <th className="py-2 pr-3">Avg Risk</th>
            <th className="py-2">Avg AI</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {items.slice(0, 8).map((item) => (
            <tr key={item.officer_id}>
              <td className="py-2 pr-3 font-medium text-slate-800">{item.officer_name}</td>
              <td className="py-2 pr-3">{item.investigations}</td>
              <td className="py-2 pr-3">{item.verified_vehicles}</td>
              <td className="py-2 pr-3">{item.high_risk_vehicles}</td>
              <td className="py-2 pr-3">{Math.round(item.average_risk_score * 100)}/100</td>
              <td className="py-2">{item.average_ai_confidence != null ? `${Math.round(item.average_ai_confidence * 100)}%` : "�"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function StationTable({ items }: { items: StationPerformanceItem[] }) {
  if (items.length === 0) {
    return <p className="text-sm text-slate-500">No station data available.</p>;
  }
  return (
    <div className="table-scroll overflow-x-auto">
      <table className="min-w-full text-sm">
        <thead className="text-left text-xs uppercase tracking-wide text-slate-500">
          <tr>
            <th className="py-2 pr-3">Station</th>
            <th className="py-2 pr-3">Investigations</th>
            <th className="py-2 pr-3">Verified</th>
            <th className="py-2 pr-3">High Risk</th>
            <th className="py-2 pr-3">Avg Risk</th>
            <th className="py-2">Avg AI</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {items.slice(0, 8).map((item) => (
            <tr key={item.station_name}>
              <td className="py-2 pr-3 font-medium text-slate-800">{item.station_name}</td>
              <td className="py-2 pr-3">{item.investigations}</td>
              <td className="py-2 pr-3">{item.verified_vehicles}</td>
              <td className="py-2 pr-3">{item.high_risk_vehicles}</td>
              <td className="py-2 pr-3">{Math.round(item.average_risk_score * 100)}/100</td>
              <td className="py-2">{item.average_ai_confidence != null ? `${Math.round(item.average_ai_confidence * 100)}%` : "�"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

interface Props {
  riskDistribution: DistributionItem[];
  vehicleTypeDistribution: DistributionItem[];
  brandDistribution: DistributionItem[];
  officerPerformance: OfficerPerformanceItem[];
  stationPerformance: StationPerformanceItem[];
  verificationStatusDistribution: DistributionItem[];
  dailyTrend: DailyInvestigationTrendPoint[];
  weeklyTrend: PeriodInvestigationTrendPoint[];
  monthlyTrend: PeriodInvestigationTrendPoint[];
}

export function InvestigationReportsCharts({
  riskDistribution,
  vehicleTypeDistribution,
  brandDistribution,
  officerPerformance,
  stationPerformance,
  verificationStatusDistribution,
  dailyTrend,
  weeklyTrend,
  monthlyTrend,
}: Props) {
  return (
    <div className="grid gap-6 xl:grid-cols-2">
      <Card title="Risk Distribution" description="Breakdown of filtered investigations by risk level.">
        <DistributionList items={riskDistribution} />
      </Card>
      <Card title="Vehicle Type Distribution" description="Filtered registry-linked vehicle types.">
        <DistributionList items={vehicleTypeDistribution} />
      </Card>
      <Card title="Brand Distribution" description="Filtered registry-linked brands.">
        <DistributionList items={brandDistribution} />
      </Card>
      <Card title="Verification Status Distribution" description="Registry verification outcomes in the filtered result set.">
        <DistributionList items={verificationStatusDistribution} />
      </Card>
      <Card title="Daily Investigation Trend" description="Last 14 daily points from the current result set.">
        <TrendBars items={dailyTrend} />
      </Card>
      <Card title="Weekly Investigation Trend" description="Weekly reporting trend for the filtered result set.">
        <PeriodTrendBars items={weeklyTrend} labelFormatter={(value) => value.replace("-", " ")} />
      </Card>
      <Card title="Monthly Investigation Trend" description="Monthly reporting trend for the filtered result set.">
        <PeriodTrendBars items={monthlyTrend} />
      </Card>
      <Card
        title="Officer Performance"
        description="Investigation throughput and quality indicators by officer."
      >
        <OfficerTable items={officerPerformance} />
      </Card>
      <Card
        title="Station Performance"
        description="Investigation throughput and quality indicators by station."
      >
        <StationTable items={stationPerformance} />
      </Card>
    </div>
  );
}
