import { ScanHistoryFiltersBar } from "@/components/features/history/ScanHistoryFiltersBar";
import { ScanHistoryTable } from "@/components/features/history/ScanHistoryTable";
import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { LoadingState } from "@/components/ui/LoadingState";
import { PageHeader } from "@/components/ui/PageHeader";
import { useScanHistory } from "@/hooks/history/useScanHistory";
import { AppLayout } from "@/layouts/AppLayout";
import { DEFAULT_SCAN_HISTORY_FILTERS } from "@/lib/scanHistoryFilters";
import { hasRole } from "@/lib/rbac";
import { OfficerInvestigationsPage } from "@/pages/policeOfficer/OfficerInvestigationsPage";
import { ChevronLeft, ChevronRight } from "lucide-react";

export function ScanHistoryPage() {
  if (hasRole("POLICE_OFFICER")) {
    return <OfficerInvestigationsPage />;
  }

  const {
    items,
    page,
    totalPages,
    totalItems,
    loading,
    error,
    filters,
    setFilters,
    setPage,
  } = useScanHistory();

  return (
    <AppLayout>
      <div className="space-y-6">
        <PageHeader
          badge="Records"
          title="Scan History"
          description="Browse completed scans and filter by date, officer, risk level, or vehicle number."
        />

        <ScanHistoryFiltersBar
          filters={filters}
          onApply={(nextFilters) => {
            setPage(1);
            setFilters(nextFilters);
          }}
          onReset={() => {
            setPage(1);
            setFilters({ ...DEFAULT_SCAN_HISTORY_FILTERS });
          }}
        />

        {loading && <LoadingState label="Loading scan history…" />}

        {error && !loading && (
          <Alert variant="warning" title="Unable to Load History">
            {error} — ensure the backend is running and you are logged in.
          </Alert>
        )}

        {!loading && !error && (
          <div className="animate-fade-in space-y-4">
            <p className="text-sm text-slate-500">
              Showing {items.length} of {totalItems} scans
            </p>
            <ScanHistoryTable items={items} />
            {totalPages > 1 && (
              <div className="flex items-center justify-between rounded-2xl border border-slate-200 bg-white px-4 py-3 shadow-soft">
                <Button
                  variant="secondary"
                  size="sm"
                  disabled={page <= 1}
                  onClick={() => setPage(page - 1)}
                  icon={<ChevronLeft className="h-4 w-4" />}
                >
                  Previous
                </Button>
                <span className="text-sm text-slate-500">
                  Page {page} of {totalPages}
                </span>
                <Button
                  variant="secondary"
                  size="sm"
                  disabled={page >= totalPages}
                  onClick={() => setPage(page + 1)}
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
