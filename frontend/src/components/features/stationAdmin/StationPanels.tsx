import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import type { StationAdminDashboardData, StationAdminNotification, StationAdminProfileData } from "@/types/api/stationAdmin";

export function StationDashboardPanels({ data }: { data: StationAdminDashboardData }) {
  const stats = [
    ["Today's Investigations", data.summary.todays_investigations],
    ["This Week's Investigations", data.summary.weekly_investigations],
    ["This Month's Investigations", data.summary.monthly_investigations],
    ["High Risk Vehicles", data.summary.high_risk_vehicles],
    ["Verified Vehicles", data.summary.verified_vehicles],
    ["Pending Investigations", data.summary.pending_investigations],
  ] as const;
  return <div className="space-y-6"><div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">{stats.map(([label, value]) => <Card key={label}><p className="text-sm text-slate-500">{label}</p><p className="mt-2 font-mono text-3xl font-bold text-brand">{value}</p></Card>)}</div><div className="grid gap-6 lg:grid-cols-3"><Card title="Recent Investigations" className="lg:col-span-2"><ul className="space-y-3">{data.recent_investigations.map((item) => <li key={item.investigation_id} className="flex items-center justify-between rounded-lg border border-slate-100 px-3 py-2"><div><p className="font-mono text-sm font-semibold">{item.registration_number}</p><p className="text-xs text-slate-500">{item.officer_name}</p></div><div className="text-right"><Badge variant={item.risk_level === "high" || item.risk_level === "critical" ? "danger" : "info"}>{item.risk_level}</Badge><p className="mt-1 text-xs text-slate-500">{new Date(item.scanned_at).toLocaleString()}</p></div></li>)}</ul></Card><Card title="High Risk Panel"><ul className="space-y-3">{data.high_risk_vehicles.map((item) => <li key={`${item.registration_number}-${item.occurred_at}`} className="rounded-lg border border-red-100 bg-red-50 px-3 py-2"><p className="font-mono text-sm font-semibold text-red-700">{item.registration_number}</p><p className="text-xs text-slate-600">{item.reason}</p><p className="mt-1 text-xs text-slate-500">{item.officer_name} · {new Date(item.occurred_at).toLocaleString()}</p></li>)}</ul></Card></div><Card title="Recent Officer Activity"><ul className="space-y-3">{data.recent_officer_activity.map((item) => <li key={item.activity_id} className="flex items-center justify-between rounded-lg border border-slate-100 px-3 py-2"><div><p className="text-sm font-medium text-slate-900">{item.officer_name}</p><p className="text-xs text-slate-500">{item.description}</p></div><div className="text-right"><Badge variant={item.status === "suspicious" ? "danger" : "info"}>{item.status}</Badge><p className="mt-1 text-xs text-slate-500">{new Date(item.occurred_at).toLocaleString()}</p></div></li>)}</ul></Card></div>;
}

export function StationNotificationsList({ items }: { items: StationAdminNotification[] }) {
  return <Card title="Notifications"><ul className="space-y-3">{items.map((item) => <li key={item.notification_id} className="rounded-xl border border-slate-100 bg-white px-4 py-3"><div className="flex items-center justify-between"><p className="font-medium text-slate-900">{item.title}</p><Badge variant={item.category === "High Risk Vehicle" ? "danger" : item.category === "Officer Deactivated" ? "warning" : "info"}>{item.category}</Badge></div><p className="mt-1 text-sm text-slate-600">{item.message}</p><p className="mt-2 text-xs text-slate-400">{new Date(item.occurred_at).toLocaleString()}</p></li>)}</ul></Card>;
}

export function StationProfileCard({ profile }: { profile: StationAdminProfileData }) {
  return <Card title="Station Profile"><dl className="divide-y divide-slate-100">{[["Station", profile.station_name],["Code", profile.station_code],["Address", profile.address],["Phone", profile.phone_number ?? "-"],["Email", profile.email ?? "-"],["District", profile.district],["State", profile.state],["Station Type", profile.station_type],["Admin", `${profile.admin_name} · ${profile.admin_rank}`]].map(([label, value]) => <div key={label} className="flex justify-between gap-6 py-3 text-sm"><dt className="text-slate-500">{label}</dt><dd className="text-right font-medium text-slate-900">{value}</dd></div>)}</dl></Card>;
}
