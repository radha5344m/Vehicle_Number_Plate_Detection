import { useCallback, useEffect, useState } from "react";
import {
  getReadNotificationIds,
  markAllNotificationsRead,
  markNotificationRead,
} from "@/lib/superAdminProfile";
import { superAdminService } from "@/services/superAdminService";
import type { SuperAdminNotification } from "@/types/api/superAdmin";

export function useSuperAdminNotifications() {
  const [items, setItems] = useState<SuperAdminNotification[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(() => {
    setLoading(true);
    setError(null);
    superAdminService
      .getNotifications()
      .then(setItems)
      .catch((err) => {
        setError(err instanceof Error ? err.message : "Failed to load notifications");
      })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const markRead = useCallback((notificationId: string) => {
    markNotificationRead(notificationId);
    setItems((current) =>
      current.map((item) =>
        item.id === notificationId ? { ...item, is_read: true } : item,
      ),
    );
  }, []);

  const markAllRead = useCallback(() => {
    const unreadIds = items.filter((item) => !item.is_read).map((item) => item.id);
    if (unreadIds.length === 0) return;
    markAllNotificationsRead(unreadIds);
    setItems((current) => current.map((item) => ({ ...item, is_read: true })));
  }, [items]);

  const unreadCount = items.filter((item) => !item.is_read).length;

  return {
    items,
    loading,
    error,
    unreadCount,
    refresh: load,
    markRead,
    markAllRead,
    readIds: getReadNotificationIds(),
  };
}
