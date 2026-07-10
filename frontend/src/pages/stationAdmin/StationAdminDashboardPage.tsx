import { Alert } from "@/components/ui/Alert";
import { LoadingState } from "@/components/ui/LoadingState";
import { PageHeader } from "@/components/ui/PageHeader";
import { StationDashboardPanels } from "@/components/features/stationAdmin/StationPanels";
import { useStationAdminDashboard } from "@/hooks/stationAdmin/useStationAdmin";
import { AppLayout } from "@/layouts/AppLayout";

export function StationAdminDashboardPage() {
  const { data, loading, error } = useStationAdminDashboard();
  return <AppLayout><div className="space-y-6"><PageHeader badge="Station Operations" title="Station Dashboard" description="Real-time investigation, risk, and officer activity metrics for your police station." />{loading && <LoadingState label="Loading station dashboard..." fullHeight />}{error && !loading && <Alert variant="warning" title="Dashboard Unavailable">{error}</Alert>}{data && !loading && <StationDashboardPanels data={data} />}</div></AppLayout>;
}
