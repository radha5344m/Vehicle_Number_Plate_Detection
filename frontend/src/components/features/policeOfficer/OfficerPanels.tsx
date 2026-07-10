import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import type {
  PoliceOfficerDashboardData,
  PoliceOfficerNotification,
  PoliceOfficerProfileData,
} from "@/types/api/policeOfficer";

export function PoliceOfficerDashboardPanels({ data }: { data: PoliceOfficerDashboardData }) {
  const stats = [
    ["Today's Verifications", data.summary.todays_verifications],
    ["This Week's Verifications", data.summary.weekly_verifications],
    ["This Month's Verifications", data.summary.monthly_verifications],
    ["High Risk Vehicles Found", data.summary.high_risk_vehicles_found],
    [
      "Average AI Confidence",
      data.summary.average_ai_confidence != null
        ? `${Math.round(data.summary.average_ai_confidence * 100)}%`
        : "—",
    ],
    [
      "Average Risk Score",
      data.summary.average_risk_score != null
        ? `${Math.round(data.summary.average_risk_score * 100)}/100`
        : "—",
    ],
  ] as const;

  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {stats.map(([label, value]) => (
          <Card key={label}>
            <p className="text-sm text-slate-500">{label}</p>
            <p className="mt-2 font-mono text-3xl font-bold text-brand">{value}</p>
          </Card>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card title="Recent Investigations">
          <ul className="space-y-3">
            {data.recent_investigations.map((item) => (
              <li
                key={item.investigation_id}
                className="flex items-center justify-between rounded-lg border border-slate-100 px-3 py-2"
              >
                <div>
                  <p className="font-mono text-sm font-semibold">{item.registration_number}</p>
                  <p className="text-xs text-slate-500">{item.vehicle_type ?? "Unknown vehicle type"}</p>
                </div>
                <div className="text-right">
                  <Badge
                    variant={
                      item.risk_level === "high" || item.risk_level === "critical"
                        ? "danger"
                        : "info"
                    }
                  >
                    {item.risk_level}
                  </Badge>
                  <p className="mt-1 text-xs text-slate-500">
                    {new Date(item.scanned_at).toLocaleString()}
                  </p>
                </div>
              </li>
            ))}
          </ul>
        </Card>

        <Card title="Recent Activity">
          <ul className="space-y-3">
            {data.recent_activity.map((item) => (
              <li
                key={item.activity_id}
                className="flex items-center justify-between rounded-lg border border-slate-100 px-3 py-2"
              >
                <div>
                  <p className="text-sm font-medium text-slate-900">{item.description}</p>
                  <p className="text-xs text-slate-500">
                    {new Date(item.occurred_at).toLocaleString()}
                  </p>
                </div>
                <Badge variant={item.status === "suspicious" ? "danger" : "info"}>
                  {item.status}
                </Badge>
              </li>
            ))}
          </ul>
        </Card>
      </div>
    </div>
  );
}

export function PoliceOfficerNotificationsList({
  items,
}: {
  items: PoliceOfficerNotification[];
}) {
  return (
    <Card title="Notifications">
      <ul className="space-y-3">
        {items.map((item) => (
          <li
            key={item.notification_id}
            className="rounded-xl border border-slate-100 bg-white px-4 py-3"
          >
            <div className="flex items-center justify-between gap-3">
              <p className="font-medium text-slate-900">{item.title}</p>
              <Badge
                variant={
                  item.category === "High Risk Vehicle Alert"
                    ? "danger"
                    : item.category === "Investigation Completed"
                      ? "success"
                      : "info"
                }
              >
                {item.category}
              </Badge>
            </div>
            <p className="mt-1 text-sm text-slate-600">{item.message}</p>
            <p className="mt-2 text-xs text-slate-400">
              {new Date(item.occurred_at).toLocaleString()}
            </p>
          </li>
        ))}
      </ul>
    </Card>
  );
}

export function PoliceOfficerProfileCard({ profile }: { profile: PoliceOfficerProfileData }) {
  return (
    <Card title="Officer Information">
      <dl className="divide-y divide-slate-100">
        {[
          ["Officer Name", profile.officer_name],
          ["Employee ID", profile.employee_id],
          ["Badge Number", profile.badge_number],
          ["Rank", profile.rank],
          ["Station", `${profile.station_name} (${profile.station_code})`],
          ["Phone", profile.phone_number ?? "-"],
          ["Email", profile.email],
          ["Username", profile.username],
        ].map(([label, value]) => (
          <div key={label} className="flex justify-between gap-6 py-3 text-sm">
            <dt className="text-slate-500">{label}</dt>
            <dd className="text-right font-medium text-slate-900">{value}</dd>
          </div>
        ))}
      </dl>
    </Card>
  );
}

export function InvestigationDetailsCard({
  item,
  onDownload,
}: {
  item: {
    investigation_id: string;
    registration_number: string;
    vehicle: string | null;
    brand: string | null;
    model: string | null;
    vehicle_type?: string | null;
    risk_score: number;
    risk_level: string;
    verification_status: string | null;
    ai_confidence: number | null;
    verification_message?: string | null;
  };
  onDownload: () => void;
}) {
  return (
    <Card title="Investigation Details">
      <div className="grid gap-3 md:grid-cols-2">
        {[
          ["Investigation ID", item.investigation_id],
          ["Registration", item.registration_number],
          ["Vehicle", item.vehicle ?? "-"],
          ["Brand", item.brand ?? "-"],
          ["Model", item.model ?? "-"],
          ["Vehicle Type", item.vehicle_type ?? "-"],
          ["Risk Level", item.risk_level],
          ["Risk Score", `${Math.round(item.risk_score * 100)}/100`],
          ["Verification", item.verification_status ?? "-"],
          [
            "AI Confidence",
            item.ai_confidence != null ? `${Math.round(item.ai_confidence * 100)}%` : "-",
          ],
        ].map(([label, value]) => (
          <div key={label} className="rounded-xl border border-slate-100 bg-slate-50 px-4 py-3">
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{label}</p>
            <p className="mt-1 text-sm font-medium text-slate-900">{value}</p>
          </div>
        ))}
      </div>
      {item.verification_message && (
        <div className="mt-4 rounded-xl border border-slate-100 bg-slate-50 px-4 py-3">
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
            Verification Message
          </p>
          <p className="mt-1 text-sm text-slate-700">{item.verification_message}</p>
        </div>
      )}
      <div className="mt-4">
        <Button onClick={onDownload}>Download Report</Button>
      </div>
    </Card>
  );
}
