import { Alert } from "@/components/ui/Alert";
import { LoadingState } from "@/components/ui/LoadingState";
import { PageHeader } from "@/components/ui/PageHeader";
import { PoliceOfficerDashboardPanels } from "@/components/features/policeOfficer/OfficerPanels";
import { usePoliceOfficerDashboard } from "@/hooks/policeOfficer/usePoliceOfficer";
import { AppLayout } from "@/layouts/AppLayout";

export function OfficerDashboardPage() {
  const { data, loading, error } = usePoliceOfficerDashboard();

  return (
    <AppLayout>
      <div className="space-y-6">
        <PageHeader
          badge="Field Operations"
          title="Officer Dashboard"
          description="Your real-time verification performance, recent investigations, and activity updates."
        />
        {loading && <LoadingState label="Loading officer dashboard..." fullHeight />}
        {error && !loading && (
          <Alert variant="warning" title="Dashboard Unavailable">
            {error}
          </Alert>
        )}
        {data && !loading && <PoliceOfficerDashboardPanels data={data} />}
      </div>
    </AppLayout>
  );
}
