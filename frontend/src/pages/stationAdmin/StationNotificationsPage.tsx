import { Alert } from "@/components/ui/Alert";
import { LoadingState } from "@/components/ui/LoadingState";
import { PageHeader } from "@/components/ui/PageHeader";
import { StationNotificationsList } from "@/components/features/stationAdmin/StationPanels";
import { useStationNotifications } from "@/hooks/stationAdmin/useStationAdmin";
import { AppLayout } from "@/layouts/AppLayout";

export function StationNotificationsPage() {
  const { items, loading, error } = useStationNotifications();
  return <AppLayout><div className="space-y-6"><PageHeader badge="Alerts" title="Notifications" description="High risk, officer lifecycle, and system alerts for your station." />{loading && <LoadingState label="Loading notifications..." fullHeight />}{error && !loading && <Alert variant="warning" title="Notifications Unavailable">{error}</Alert>}{!loading && !error && <StationNotificationsList items={items} />}</div></AppLayout>;
}
