import { Building2, ChevronLeft, ChevronRight } from "lucide-react";
import { useState } from "react";

import { StationsFiltersBar } from "@/components/features/stations/StationsFiltersBar";
import { StationManagementPanel } from "@/components/features/stations/StationManagementPanel";
import { StationsTable } from "@/components/features/stations/StationsTable";
import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { LoadingState } from "@/components/ui/LoadingState";
import { PageHeader } from "@/components/ui/PageHeader";
import { useStations } from "@/hooks/stations/useStations";
import { AppLayout } from "@/layouts/AppLayout";
import { hasPermission, hasRole } from "@/lib/rbac";
import { stationsService } from "@/services/stationsService";
import type { CreateStationRequest, StationItem, UpdateStationRequest } from "@/types/api/stations";

const INITIAL_FILTERS = {
  page: 1,
  page_size: 20,
  sort_by: "created_at",
  sort_desc: true,
} as const;

export function PoliceStationsPage() {
  const isSuperAdmin = hasRole("SUPER_ADMIN");
  const canManageStations = hasPermission("stations");
  const { data, loading, error, filters, setFilters, setPage, refresh } = useStations(INITIAL_FILTERS);
  const [panelMode, setPanelMode] = useState<"create" | "edit" | null>(null);
  const [selectedStation, setSelectedStation] = useState<StationItem | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);

  if (!isSuperAdmin) {
    return (
      <AppLayout>
        <Alert variant="warning" title="Access Denied">Only SUPER_ADMIN can access Police Station Management.</Alert>
      </AppLayout>
    );
  }

  async function handleCreate(payload: CreateStationRequest) {
    setActionError(null);
    await stationsService.create(payload);
    setActionSuccess("Station created successfully.");
    setPanelMode(null);
    refresh();
  }

  async function handleUpdate(stationId: string, payload: UpdateStationRequest) {
    setActionError(null);
    await stationsService.update(stationId, payload);
    setActionSuccess("Station updated successfully.");
    setPanelMode(null);
    refresh();
  }

  async function handleToggleStatus(station: StationItem) {
    if (!window.confirm(`${station.status === "active" ? "Deactivate" : "Activate"} ${station.station_name}?`)) return;
    await stationsService.changeStatus(station.station_id, station.status === "active" ? "inactive" : "active");
    setActionSuccess(`Station ${station.status === "active" ? "deactivated" : "activated"} successfully.`);
    refresh();
  }

  async function handleDelete(station: StationItem) {
    if (!window.confirm(`Soft delete ${station.station_name}?`)) return;
    await stationsService.delete(station.station_id);
    setActionSuccess("Station deleted successfully.");
    refresh();
  }

  return (
    <AppLayout>
      <div className="space-y-6">
        <PageHeader
          badge="Administration"
          title="Police Stations"
          description="Manage district police stations with enterprise search, filters, activation controls, and clean master data governance."
          actions={
            canManageStations ? (
              <Button icon={<Building2 className="h-4 w-4" />} onClick={() => { setSelectedStation(null); setPanelMode("create"); }}>
                Create Station
              </Button>
            ) : undefined
          }
        />

        <StationsFiltersBar filters={filters} onApply={(next) => setFilters(next)} onReset={() => setFilters({ ...INITIAL_FILTERS })} />

        {actionSuccess && <Alert variant="success" title="Success">{actionSuccess}</Alert>}
        {actionError && <Alert variant="error" title="Action Failed">{actionError}</Alert>}

        {panelMode && (
          <StationManagementPanel
            mode={panelMode}
            station={selectedStation}
            onClose={() => setPanelMode(null)}
            onCreate={async (payload) => {
              try {
                await handleCreate(payload);
              } catch (err) {
                setActionError(err instanceof Error ? err.message : "Create failed");
              }
            }}
            onUpdate={async (stationId, payload) => {
              try {
                await handleUpdate(stationId, payload);
              } catch (err) {
                setActionError(err instanceof Error ? err.message : "Update failed");
              }
            }}
          />
        )}

        {loading && <LoadingState label="Loading stations..." fullHeight />}
        {error && !loading && <Alert variant="warning" title="Unable to Load Stations">{error}</Alert>}

        {data && !loading && (
          <div className="space-y-4">
            <p className="text-sm text-slate-500">Showing {data.items.length} of {data.pagination.total_items} stations</p>
            <StationsTable
              items={data.items}
              onEdit={(station) => { setSelectedStation(station); setPanelMode("edit"); }}
              onToggleStatus={(station) => void handleToggleStatus(station)}
              onDelete={(station) => void handleDelete(station)}
              canManage={canManageStations}
            />
            {data.pagination.total_pages > 1 && (
              <div className="flex items-center justify-between rounded-2xl border border-slate-200 bg-white px-4 py-3 shadow-soft">
                <Button variant="secondary" size="sm" disabled={data.pagination.page <= 1} onClick={() => setPage(data.pagination.page - 1)} icon={<ChevronLeft className="h-4 w-4" />}>Previous</Button>
                <span className="text-sm text-slate-500">Page {data.pagination.page} of {data.pagination.total_pages}</span>
                <Button variant="secondary" size="sm" disabled={data.pagination.page >= data.pagination.total_pages} onClick={() => setPage(data.pagination.page + 1)} icon={<ChevronRight className="h-4 w-4" />}>Next</Button>
              </div>
            )}
          </div>
        )}
      </div>
    </AppLayout>
  );
}
