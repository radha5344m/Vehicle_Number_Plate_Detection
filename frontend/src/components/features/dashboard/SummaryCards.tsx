import { Car, ScanLine, ShieldAlert, Timer } from "lucide-react";
import type { DashboardSummary } from "@/types/api/dashboard";
import { Card } from "@/components/ui/Card";

interface SummaryCardsProps {
  summary: DashboardSummary;
}

const metrics = [
  {
    key: "total_scans" as const,
    label: "Total Scans",
    description: "Completed verifications",
    accent: "text-brand",
    bg: "bg-brand-soft",
    icon: ScanLine,
  },
  {
    key: "verified_vehicles" as const,
    label: "Verified Vehicles",
    description: "Registry matches",
    accent: "text-green-600",
    bg: "bg-green-50",
    icon: Car,
  },
  {
    key: "suspicious_vehicles" as const,
    label: "Suspicious Vehicles",
    description: "High / critical risk",
    accent: "text-red-600",
    bg: "bg-red-50",
    icon: ShieldAlert,
  },
  {
    key: "pending_verification" as const,
    label: "Pending Verification",
    description: "No registry match",
    accent: "text-amber-600",
    bg: "bg-amber-50",
    icon: Timer,
  },
];

export function SummaryCards({ summary }: SummaryCardsProps) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {metrics.map(({ key, label, description, accent, bg, icon: Icon }) => (
        <Card key={key} className="group">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm font-medium text-slate-500">{label}</p>
              <p className={`mt-2 font-mono text-3xl font-bold tracking-tight ${accent}`}>
                {summary[key].toLocaleString()}
              </p>
              <p className="mt-1 text-xs text-slate-400">{description}</p>
            </div>
            <div
              className={`flex h-11 w-11 items-center justify-center rounded-xl ${bg} transition-transform duration-300 group-hover:scale-110`}
            >
              <Icon className={`h-5 w-5 ${accent}`} aria-hidden />
            </div>
          </div>
        </Card>
      ))}
    </div>
  );
}
