import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Card } from "@/components/ui/Card";
import { ChartCard } from "@/components/features/analytics/ChartCard";
import { ExecutiveDashboardFiltersPanel } from "@/components/features/dashboard/ExecutiveDashboardFiltersPanel";
import type {
  ActivityFeedItem,
  ChartPoint,
  ExecutiveDashboardData,
  ExecutiveDashboardFilters,
  LeaderboardItem,
} from "@/types/api/executiveDashboard";

const COLORS = ["#2563eb", "#0f766e", "#0891b2", "#7c3aed", "#f59e0b", "#ef4444", "#64748b"];

function RechartBar({ data }: { data: ChartPoint[] }) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={data}>
        <CartesianGrid stroke="#e2e8f0" strokeDasharray="3 3" vertical={false} />
        <XAxis dataKey="label" tick={{ fill: "#64748b", fontSize: 11 }} stroke="#cbd5e1" />
        <YAxis tick={{ fill: "#64748b", fontSize: 11 }} stroke="#cbd5e1" />
        <Tooltip />
        <Bar dataKey="value" fill="#2563eb" radius={[6, 6, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

function RechartLine({ data }: { data: ChartPoint[] }) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart data={data}>
        <CartesianGrid stroke="#e2e8f0" strokeDasharray="3 3" vertical={false} />
        <XAxis dataKey="label" tick={{ fill: "#64748b", fontSize: 11 }} stroke="#cbd5e1" />
        <YAxis tick={{ fill: "#64748b", fontSize: 11 }} stroke="#cbd5e1" />
        <Tooltip />
        <Line dataKey="value" type="monotone" stroke="#2563eb" strokeWidth={2.5} dot={{ r: 3 }} />
      </LineChart>
    </ResponsiveContainer>
  );
}

function RechartPie({ data }: { data: ChartPoint[] }) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <PieChart>
        <Pie data={data} dataKey="value" nameKey="label" outerRadius={88} label>
          {data.map((item, index) => (
            <Cell key={item.label} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip />
      </PieChart>
    </ResponsiveContainer>
  );
}

function LeaderboardTable({ title, items }: { title: string; items: LeaderboardItem[] }) {
  return (
    <Card title={title}>
      <div className="space-y-3">
        {items.map((item) => (
          <div key={`${title}-${item.name}`} className="rounded-xl border border-slate-100 px-4 py-3">
            <div className="flex items-center justify-between gap-3">
              <div>
                <p className="text-sm font-semibold text-slate-900">{item.name}</p>
                <p className="text-xs text-slate-500">{item.metric}</p>
              </div>
              <div className="text-right">
                <p className="text-sm font-semibold text-brand">{Math.round(item.value * 10) / 10}</p>
                {item.secondary_value && <p className="text-xs text-slate-500">{item.secondary_value}</p>}
              </div>
            </div>
          </div>
        ))}
        {items.length === 0 && <p className="text-sm text-slate-500">No data in the selected scope.</p>}
      </div>
    </Card>
  );
}

function ActivityList({ title, items }: { title: string; items: ActivityFeedItem[] }) {
  return (
    <Card title={title}>
      <div className="space-y-3">
        {items.map((item) => (
          <div key={`${title}-${item.id}`} className="rounded-xl border border-slate-100 px-4 py-3">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="text-sm font-semibold text-slate-900">{item.title}</p>
                <p className="text-xs text-slate-500">{item.detail}</p>
              </div>
              <span className="text-xs text-slate-400">
                {new Date(item.occurred_at).toLocaleString()}
              </span>
            </div>
          </div>
        ))}
        {items.length === 0 && <p className="text-sm text-slate-500">No recent activity.</p>}
      </div>
    </Card>
  );
}

interface Props {
  data: ExecutiveDashboardData;
  filters?: ExecutiveDashboardFilters;
  onApplyFilters?: (filters: ExecutiveDashboardFilters) => void;
  onResetFilters?: () => void;
  onRefresh?: () => void;
  onExport?: (format: "pdf" | "csv" | "excel") => Promise<void>;
  showFilters?: boolean;
}

export function ExecutiveCommandCenter({
  data,
  filters = {},
  onApplyFilters,
  onResetFilters,
  onRefresh,
  onExport,
  showFilters = true,
}: Props) {
  return (
    <div className="space-y-6">
      {showFilters && onApplyFilters && onResetFilters && onRefresh && onExport && (
        <ExecutiveDashboardFiltersPanel
          filters={filters}
          onApplyFilters={onApplyFilters}
          onResetFilters={onResetFilters}
          onRefresh={onRefresh}
          onExport={onExport}
        />
      )}

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {data.kpis.map((item) => (
          <div key={item.label} className="rounded-2xl border border-blue-100 bg-gradient-to-br from-white to-blue-50 p-5 shadow-soft">
            <p className="text-sm text-slate-500">{item.label}</p>
            <p className="mt-2 text-3xl font-bold tracking-tight text-slate-900">{item.display_value}</p>
          </div>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <ChartCard title="Daily Investigation Trend" description="Completed investigations by day">
          <RechartLine data={data.daily_trend} />
        </ChartCard>
        <ChartCard title="Weekly Trend" description="Weekly investigation aggregation">
          <RechartBar data={data.weekly_trend} />
        </ChartCard>
        <ChartCard title="Monthly Trend" description="Monthly investigation aggregation">
          <RechartBar data={data.monthly_trend} />
        </ChartCard>
        <ChartCard title="Hourly Investigation Activity" description="Operational load by hour">
          <RechartBar data={data.hourly_activity} />
        </ChartCard>
        <ChartCard title="Investigation Status Distribution" description="Completed vs pending investigation states">
          <RechartPie data={data.investigation_status_distribution} />
        </ChartCard>
        <ChartCard title="Risk Distribution" description="Distribution across all risk levels">
          <RechartPie data={data.risk_distribution} />
        </ChartCard>
        <ChartCard title="Risk Trend Over Time" description="High-risk detections by day">
          <RechartLine data={data.risk_trend} />
        </ChartCard>
        <ChartCard title="Top High-Risk Registrations" description="Registrations with repeated critical activity">
          <RechartBar data={data.top_high_risk_registrations} />
        </ChartCard>
        <ChartCard title="Most Frequent Suspicious Vehicles" description="Most repeatedly suspicious registrations">
          <RechartBar data={data.frequent_suspicious_vehicles} />
        </ChartCard>
        <ChartCard title="Vehicle Type Distribution" description="Scope-level vehicle category mix">
          <RechartPie data={data.vehicle_type_distribution} />
        </ChartCard>
        <ChartCard title="Vehicle Brand Distribution" description="Most detected brands">
          <RechartBar data={data.vehicle_brand_distribution} />
        </ChartCard>
        <ChartCard title="Vehicle Color Distribution" description="Observed color distribution">
          <RechartPie data={data.vehicle_color_distribution} />
        </ChartCard>
        <ChartCard title="Registration State Distribution" description="Plate prefixes detected in scope">
          <RechartBar data={data.registration_state_distribution} />
        </ChartCard>
        <ChartCard title="Most Common Vehicle Models" description="Most frequently matched models">
          <RechartBar data={data.common_vehicle_models} />
        </ChartCard>
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <LeaderboardTable title="Top Performing Officers" items={data.top_performing_officers} />
        <LeaderboardTable title="Most Active Officers" items={data.most_active_officers} />
        <LeaderboardTable title="Officer Leaderboard" items={data.officer_leaderboard} />
        <LeaderboardTable title="Top Performing Stations" items={data.top_performing_stations} />
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <Card title="AI Metrics">
          <div className="grid gap-4 sm:grid-cols-2">
            {data.ai_metrics.map((item) => (
              <div key={item.label} className="rounded-xl border border-slate-100 px-4 py-3">
                <p className="text-sm text-slate-500">{item.label}</p>
                <p className="mt-1 text-xl font-semibold text-slate-900">{item.display_value}</p>
              </div>
            ))}
          </div>
        </Card>
        <Card title="Executive Insights">
          <div className="space-y-3">
            {data.insights.map((item) => (
              <div key={item.title} className="rounded-xl border border-blue-100 bg-blue-50/60 px-4 py-3">
                <p className="text-sm font-semibold text-brand">{item.title}</p>
                <p className="mt-1 text-sm text-slate-600">{item.detail}</p>
              </div>
            ))}
          </div>
        </Card>
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <ActivityList title="Recent Investigations" items={data.recent_investigations} />
        <ActivityList title="Recent High-Risk Alerts" items={data.recent_high_risk_alerts} />
        <ActivityList title="Recent Officer Activity" items={data.recent_officer_activity} />
        <ActivityList title="Recent Reports Generated" items={data.recent_reports_generated} />
      </div>
    </div>
  );
}
