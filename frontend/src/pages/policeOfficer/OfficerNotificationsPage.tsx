import { Alert } from "@/components/ui/Alert";
import { LoadingState } from "@/components/ui/LoadingState";
import { PageHeader } from "@/components/ui/PageHeader";
import { PoliceOfficerNotificationsList } from "@/components/features/policeOfficer/OfficerPanels";
import { usePoliceOfficerNotifications } from "@/hooks/policeOfficer/usePoliceOfficer";
import { AppLayout } from "@/layouts/AppLayout";

export function OfficerNotificationsPage() {
  const { items, loading, error } = usePoliceOfficerNotifications();

  return (
    <AppLayout>
      <div className="space-y-6">
        <PageHeader
          badge="Alerts"
          title="Notifications"
          description="Investigation completion, high risk alerts, and command center announcements for your account."
        />
        {loading && <LoadingState label="Loading notifications..." fullHeight />}
        {error && !loading && (
          <Alert variant="warning" title="Notifications Unavailable">
            {error}
          </Alert>
        )}
        {!loading && !error && <PoliceOfficerNotificationsList items={items} />}
      </div>
    </AppLayout>
  );
}
