import { ChevronLeft, ChevronRight } from "lucide-react";
import { useState } from "react";

import { InvestigationDetailsCard } from "@/components/features/policeOfficer/OfficerPanels";
import { OfficerInvestigationsTable } from "@/components/features/policeOfficer/OfficerInvestigationsTable";
import { OfficerReportsFiltersBar } from "@/components/features/policeOfficer/OfficerReportsFiltersBar";
import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { LoadingState } from "@/components/ui/LoadingState";
import { PageHeader } from "@/components/ui/PageHeader";
import { usePoliceOfficerInvestigations } from "@/hooks/policeOfficer/usePoliceOfficer";
import { AppLayout } from "@/layouts/AppLayout";
import { reportService } from "@/services/reportService";
import type { InvestigationReportListItem } from "@/types/api/investigationReports";

const INITIAL_FILTERS = {
  page: 1,
  page_size: 20,
  sort_by: "scanned_at" as const,
  sort_desc: true,
};

export function OfficerInvestigationsPage() {
  const { data, loading, error, filters, setFilters, setPage } =
    usePoliceOfficerInvestigations(INITIAL_FILTERS);
  const [selectedItem, setSelectedItem] = useState<InvestigationReportListItem | null>(null);

  async function handleDownloadReport(item: InvestigationReportListItem) {
    if (!item.report_download_url) return;
    await reportService.downloadReport(
      item.report_download_url,
      `investigation-${item.report_id ?? item.investigation_id}.pdf`,
    );
  }

  return (
    <AppLayout>
      <div className="space-y-6">
        <PageHeader
          badge="My Investigations"
          title="My Investigations"
          description="Search, filter, review, and download only the investigations created under your account."
        />
        <OfficerReportsFiltersBar
          filters={filters}
          onApply={(next) => setFilters(next)}
          onReset={() => setFilters({ ...INITIAL_FILTERS })}
          submitLabel="Search Investigations"
        />
        {selectedItem && (
          <InvestigationDetailsCard
            item={selectedItem}
            onDownload={() => void handleDownloadReport(selectedItem)}
          />
        )}
        {loading && <LoadingState label="Loading investigations..." fullHeight />}
        {error && !loading && (
          <Alert variant="warning" title="Unable to Load Investigations">
            {error}
          </Alert>
        )}
        {data && !loading && (
          <div className="space-y-4">
            <p className="text-sm text-slate-500">
              Showing {data.items.length} of {data.pagination.total_items} investigations
            </p>
            <OfficerInvestigationsTable
              items={data.items}
              onDownloadReport={(item) => void handleDownloadReport(item)}
              onViewDetails={setSelectedItem}
            />
            {data.pagination.total_pages > 1 && (
              <div className="flex items-center justify-between rounded-2xl border border-slate-200 bg-white px-4 py-3 shadow-soft">
                <Button
                  variant="secondary"
                  size="sm"
                  disabled={data.pagination.page <= 1}
                  onClick={() => setPage(data.pagination.page - 1)}
                  icon={<ChevronLeft className="h-4 w-4" />}
                >
                  Previous
                </Button>
                <span className="text-sm text-slate-500">
                  Page {data.pagination.page} of {data.pagination.total_pages}
                </span>
                <Button
                  variant="secondary"
                  size="sm"
                  disabled={data.pagination.page >= data.pagination.total_pages}
                  onClick={() => setPage(data.pagination.page + 1)}
                  icon={<ChevronRight className="h-4 w-4" />}
                >
                  Next
                </Button>
              </div>
            )}
          </div>
        )}
      </div>
    </AppLayout>
  );
}
