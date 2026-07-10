import { Alert } from "@/components/ui/Alert";
import { LoadingState } from "@/components/ui/LoadingState";
import { PageHeader } from "@/components/ui/PageHeader";
import { InvestigationReportsFiltersBar } from "@/components/features/reports/InvestigationReportsFiltersBar";
import { InvestigationReportsTable } from "@/components/features/reports/InvestigationReportsTable";
import { useStationInvestigations } from "@/hooks/stationAdmin/useStationAdmin";
import { AppLayout } from "@/layouts/AppLayout";
import { reportService } from "@/services/reportService";
import type { InvestigationReportListItem } from "@/types/api/investigationReports";

const INITIAL_FILTERS = { page: 1, page_size: 20, sort_by: "scanned_at" as const, sort_desc: true };

export function StationInvestigationsPage() {
  const { data, loading, error, filters, setFilters } = useStationInvestigations(INITIAL_FILTERS);
  async function handleDownloadReport(item: InvestigationReportListItem) { if (!item.report_download_url) return; await reportService.downloadReport(item.report_download_url, `station-investigation-${item.report_id ?? item.investigation_id}.pdf`); }
  return <AppLayout><div className="space-y-6"><PageHeader badge="Station Investigations" title="Station Investigations" description="Review all investigations created by officers in your station with enterprise filtering and report downloads." /><InvestigationReportsFiltersBar filters={filters} onApply={(next) => setFilters(next)} onReset={() => setFilters({ ...INITIAL_FILTERS })} />{loading && <LoadingState label="Loading investigations..." fullHeight />}{error && !loading && <Alert variant="warning" title="Unable to Load Investigations">{error}</Alert>}{data && !loading && <InvestigationReportsTable items={data.items} onDownloadReport={(item) => void handleDownloadReport(item)} />}</div></AppLayout>;
}
