import { ChevronLeft, ChevronRight, Download, FileSpreadsheet, FileText, Printer, RotateCcw } from "lucide-react";
import { useState } from "react";

import { InvestigationDetailsCard } from "@/components/features/policeOfficer/OfficerPanels";
import { InvestigationReportsCharts } from "@/components/features/reports/InvestigationReportsCharts";
import { InvestigationReportsFiltersBar } from "@/components/features/reports/InvestigationReportsFiltersBar";
import { InvestigationReportsSummaryCards } from "@/components/features/reports/InvestigationReportsSummaryCards";
import { InvestigationReportsTable } from "@/components/features/reports/InvestigationReportsTable";
import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { LoadingState } from "@/components/ui/LoadingState";
import { PageHeader } from "@/components/ui/PageHeader";
import { useStationReports } from "@/hooks/stationAdmin/useStationAdmin";
import { AppLayout } from "@/layouts/AppLayout";
import { reportService } from "@/services/reportService";
import { stationAdminService } from "@/services/stationAdminService";
import type { InvestigationReportListItem } from "@/types/api/investigationReports";

const INITIAL_FILTERS = { page: 1, page_size: 20, sort_by: "scanned_at" as const, sort_desc: true };

export function StationReportsPage() {
  const { data, loading, error, filters, setFilters, setPage, refresh } = useStationReports(INITIAL_FILTERS);
  const [selectedItem, setSelectedItem] = useState<InvestigationReportListItem | null>(null);

  async function handleDownloadReport(item: InvestigationReportListItem) {
    if (!item.report_download_url) return;
    await reportService.downloadReport(
      item.report_download_url,
      `station-report-${item.report_id ?? item.investigation_id}.pdf`,
    );
  }

  return (
    <AppLayout>
      <div className="space-y-6 print:space-y-4">
        <PageHeader
          badge="Station Reports"
          title="Reports"
          description="Generate station-level daily, weekly, monthly, officer, and high risk reporting with exports and printable summaries."
          actions={
            <>
              <Button variant="secondary" icon={<RotateCcw className="h-4 w-4" />} onClick={() => { setFilters({ ...INITIAL_FILTERS }); refresh(); }}>
                Reset Filters
              </Button>
              <Button variant="secondary" icon={<FileText className="h-4 w-4" />} onClick={() => void stationAdminService.exportPdf(filters)}>
                Export PDF
              </Button>
              <Button variant="secondary" icon={<FileSpreadsheet className="h-4 w-4" />} onClick={() => void stationAdminService.exportExcel(filters)}>
                Export Excel
              </Button>
              <Button variant="secondary" icon={<Download className="h-4 w-4" />} onClick={() => void stationAdminService.exportCsv(filters)}>
                Export CSV
              </Button>
              <Button variant="ghost" icon={<Printer className="h-4 w-4" />} onClick={() => window.print()}>
                Print
              </Button>
            </>
          }
        />

        <div className="print:hidden">
          <InvestigationReportsFiltersBar
            filters={filters}
            onApply={(next) => setFilters(next)}
            onReset={() => setFilters({ ...INITIAL_FILTERS })}
          />
        </div>

        {selectedItem ? (
          <InvestigationDetailsCard
            item={selectedItem}
            onDownload={() => void handleDownloadReport(selectedItem)}
          />
        ) : null}

        {loading && <LoadingState label="Loading station reports..." fullHeight />}
        {error && !loading && <Alert variant="warning" title="Unable to Load Reports">{error}</Alert>}
        {data && !loading && (
          <div className="space-y-6">
            <p className="text-sm text-slate-500">
              Showing {data.items.length} of {data.pagination.total_items} station investigations
            </p>
            <InvestigationReportsSummaryCards summary={data.summary} />
            <InvestigationReportsCharts
              riskDistribution={data.risk_distribution}
              vehicleTypeDistribution={data.vehicle_type_distribution}
              brandDistribution={data.brand_distribution}
              officerPerformance={data.officer_performance}
              stationPerformance={data.station_performance}
              verificationStatusDistribution={data.verification_status_distribution}
              dailyTrend={data.daily_investigation_trend}
              weeklyTrend={data.weekly_investigation_trend}
              monthlyTrend={data.monthly_investigation_trend}
            />
            <InvestigationReportsTable
              items={data.items}
              onDownloadReport={(item) => void handleDownloadReport(item)}
              onViewDetails={setSelectedItem}
              onPrintReport={() => window.print()}
            />
            {data.pagination.total_pages > 1 ? (
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
            ) : null}
          </div>
        )}
      </div>
    </AppLayout>
  );
}
