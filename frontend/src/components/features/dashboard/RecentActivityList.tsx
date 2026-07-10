import { Clock } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import type { RecentActivityItem } from "@/types/api/dashboard";

interface RecentActivityListProps {
  items: RecentActivityItem[];
}

const statusVariant: Record<string, "success" | "danger" | "warning" | "info" | "default"> = {
  verified: "success",
  suspicious: "danger",
  pending: "warning",
  completed: "info",
  failed: "default",
};

function formatTime(iso: string): string {
  return new Date(iso).toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function RecentActivityList({ items }: RecentActivityListProps) {
  return (
    <Card
      title="Recent Activity"
      description="Latest officer workflow events"
      icon={<Clock className="h-4 w-4" />}
    >
      <ul className="divide-y divide-slate-100">
        {items.map((item) => (
          <li
            key={item.id}
            className="-mx-2 flex flex-col gap-2 rounded-lg px-2 py-4 transition-colors hover:bg-slate-50 sm:flex-row sm:items-center sm:justify-between"
          >
            <div className="min-w-0">
              <p className="font-mono text-sm font-semibold text-slate-900">
                {item.plate_text || "—"}
              </p>
              <p className="mt-1 text-sm text-slate-500">{item.description}</p>
            </div>
            <div className="flex shrink-0 items-center gap-3">
              <Badge variant={statusVariant[item.status] ?? "default"}>
                {item.status}
              </Badge>
              <time className="text-xs text-slate-400">{formatTime(item.occurred_at)}</time>
            </div>
          </li>
        ))}
      </ul>
    </Card>
  );
}
