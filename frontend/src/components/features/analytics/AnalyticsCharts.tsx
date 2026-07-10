import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  Cell,
} from "recharts";
import type { ChartSeries, SuspiciousVehicleItem } from "@/types/api/analytics";

const CHART_COLORS = ["#2563eb", "#14b8a6", "#22c55e", "#f59e0b", "#ef4444", "#64748b"];
const GRID_STROKE = "#e2e8f0";
const AXIS_TICK = { fill: "#64748b", fontSize: 11 };
const TOOLTIP_STYLE = {
  backgroundColor: "#ffffff",
  border: "1px solid #e2e8f0",
  borderRadius: "0.5rem",
  boxShadow: "0 4px 12px rgba(15,23,42,0.08)",
} as const;
const TOOLTIP_LABEL = { color: "#0f172a", fontWeight: 600 } as const;

function toChartData(series: ChartSeries) {
  return series.labels.map((label, index) => ({
    label,
    value: series.values[index] ?? 0,
  }));
}

interface DailyScansChartProps {
  series: ChartSeries;
}

export function DailyScansChart({ series }: DailyScansChartProps) {
  const data = toChartData(series);
  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart data={data}>
        <CartesianGrid stroke={GRID_STROKE} strokeDasharray="3 3" vertical={false} />
        <XAxis dataKey="label" tick={AXIS_TICK} stroke={GRID_STROKE} />
        <YAxis allowDecimals={false} tick={AXIS_TICK} stroke={GRID_STROKE} />
        <Tooltip contentStyle={TOOLTIP_STYLE} labelStyle={TOOLTIP_LABEL} cursor={{ stroke: "#cbd5e1" }} />
        <Line type="monotone" dataKey="value" stroke="#2563eb" strokeWidth={2.5} dot={{ r: 3, fill: "#2563eb" }} activeDot={{ r: 5 }} />
      </LineChart>
    </ResponsiveContainer>
  );
}

interface RiskDistributionChartProps {
  series: ChartSeries;
}

export function RiskDistributionChart({ series }: RiskDistributionChartProps) {
  const data = toChartData(series);
  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={data}>
        <CartesianGrid stroke={GRID_STROKE} strokeDasharray="3 3" vertical={false} />
        <XAxis dataKey="label" tick={AXIS_TICK} stroke={GRID_STROKE} />
        <YAxis allowDecimals={false} tick={AXIS_TICK} stroke={GRID_STROKE} />
        <Tooltip contentStyle={TOOLTIP_STYLE} labelStyle={TOOLTIP_LABEL} cursor={{ fill: "rgba(37,99,235,0.06)" }} />
        <Bar dataKey="value" fill="#14b8a6" radius={[6, 6, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

interface VehicleTypesChartProps {
  series: ChartSeries;
}

export function VehicleTypesChart({ series }: VehicleTypesChartProps) {
  const data = toChartData(series);
  return (
    <ResponsiveContainer width="100%" height="100%">
      <PieChart>
        <Pie data={data} dataKey="value" nameKey="label" cx="50%" cy="50%" outerRadius={90} label>
          {data.map((entry, index) => (
            <Cell key={entry.label} fill={CHART_COLORS[index % CHART_COLORS.length]} />
          ))}
        </Pie>
        <Tooltip contentStyle={TOOLTIP_STYLE} labelStyle={TOOLTIP_LABEL} />
      </PieChart>
    </ResponsiveContainer>
  );
}

interface SuspiciousVehiclesChartProps {
  items: SuspiciousVehicleItem[];
}

export function SuspiciousVehiclesChart({ items }: SuspiciousVehiclesChartProps) {
  const data = items.map((item) => ({
    label: item.plate_text,
    value: item.scan_count,
    risk: item.risk_level,
  }));

  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={data}>
        <CartesianGrid stroke={GRID_STROKE} strokeDasharray="3 3" vertical={false} />
        <XAxis dataKey="label" tick={AXIS_TICK} stroke={GRID_STROKE} />
        <YAxis allowDecimals={false} tick={AXIS_TICK} stroke={GRID_STROKE} />
        <Tooltip contentStyle={TOOLTIP_STYLE} labelStyle={TOOLTIP_LABEL} cursor={{ fill: "rgba(239,68,68,0.06)" }} />
        <Bar dataKey="value" fill="#ef4444" radius={[6, 6, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

interface OfficerActivityChartProps {
  series: ChartSeries;
}

export function OfficerActivityChart({ series }: OfficerActivityChartProps) {
  const data = toChartData(series);
  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={data} layout="vertical">
        <CartesianGrid stroke={GRID_STROKE} strokeDasharray="3 3" horizontal={false} />
        <XAxis type="number" allowDecimals={false} tick={AXIS_TICK} stroke={GRID_STROKE} />
        <YAxis type="category" dataKey="label" width={100} tick={AXIS_TICK} stroke={GRID_STROKE} />
        <Tooltip contentStyle={TOOLTIP_STYLE} labelStyle={TOOLTIP_LABEL} cursor={{ fill: "rgba(37,99,235,0.06)" }} />
        <Bar dataKey="value" fill="#2563eb" radius={[0, 6, 6, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
