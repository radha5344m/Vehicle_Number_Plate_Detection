import { BellOff, CheckCheck } from "lucide-react";

import { Badge } from "@/components/ui/Badge";
import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { LoadingState } from "@/components/ui/LoadingState";
import { PageHeader } from "@/components/ui/PageHeader";
import { useSuperAdminNotifications } from "@/hooks/superAdmin/useSuperAdminNotifications";
import { AppLayout } from "@/layouts/AppLayout";

function NotificationCategoryBadge({ category }: { category: string }) {
  const normalized = category.toLowerCase();
  const variant =
    normalized.includes("risk") || normalized.includes("alert")
      ? "danger"
      : normalized.includes("report")
        ? "success"
        : "info";

  return <Badge variant={variant}>{category}</Badge>;
}

export function SuperAdminNotificationsPage() {
  const { items, loading, error, unreadCount, markRead, markAllRead } = useSuperAdminNotifications();

  return (
    <AppLayout>
      <div className="space-y-6">
        <PageHeader
          badge="Alerts"
          title="Notifications"
          description="System-wide operational alerts, high-risk detections, and command center activity."
        />

        {!loading && !error && items.length > 0 && (
          <div className="flex flex-wrap items-center justify-between gap-3">
            <p className="text-sm text-slate-600">
              {unreadCount > 0
                ? `${unreadCount} unread notification${unreadCount === 1 ? "" : "s"}`
                : "All notifications are read"}
            </p>
            {unreadCount > 0 && (
              <Button type="button" variant="secondary" onClick={markAllRead}>
                <CheckCheck className="h-4 w-4" />
                Mark all as read
              </Button>
            )}
          </div>
        )}

        {loading && <LoadingState label="Loading notifications..." fullHeight />}

        {error && !loading && (
          <Alert variant="warning" title="Notifications Unavailable">
            {error}
          </Alert>
        )}

        {!loading && !error && items.length === 0 && (
          <Card>
            <div className="flex flex-col items-center justify-center gap-3 py-16 text-center">
              <div className="flex h-14 w-14 items-center justify-center rounded-full bg-slate-100 text-slate-400">
                <BellOff className="h-7 w-7" />
              </div>
              <div>
                <p className="text-base font-semibold text-slate-900">No notifications yet</p>
                <p className="mt-1 text-sm text-slate-500">
                  System alerts and operational updates will appear here when available.
                </p>
              </div>
            </div>
          </Card>
        )}

        {!loading && !error && items.length > 0 && (
          <Card title="Notification Center">
            <ul className="space-y-3">
              {items.map((item) => (
                <li
                  key={item.id}
                  className={`rounded-xl border px-4 py-4 transition ${
                    item.is_read
                      ? "border-slate-100 bg-white"
                      : "border-blue-100 bg-blue-50/40"
                  }`}
                >
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div className="min-w-0 flex-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <p className="font-semibold text-slate-900">{item.title}</p>
                        {!item.is_read && <Badge variant="info">Unread</Badge>}
                      </div>
                      <p className="mt-1 text-sm text-slate-600">{item.description}</p>
                      <p className="mt-2 text-xs text-slate-400">
                        {new Date(item.occurred_at).toLocaleString()}
                      </p>
                    </div>
                    <div className="flex flex-col items-end gap-2">
                      <NotificationCategoryBadge category={item.category} />
                      {!item.is_read && (
                        <Button type="button" size="sm" variant="ghost" onClick={() => markRead(item.id)}>
                          Mark as read
                        </Button>
                      )}
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </Card>
        )}
      </div>
    </AppLayout>
  );
}
