import { useMemo, useState } from "react";
import { Copy, Printer, UserPlus } from "lucide-react";

import {
  StationOfficerFiltersBar,
  StationOfficerPanel,
  StationOfficersTable,
} from "@/components/features/stationAdmin/OfficerManagement";
import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { LoadingState } from "@/components/ui/LoadingState";
import { PageHeader } from "@/components/ui/PageHeader";
import { useStationOfficers, useStationProfile } from "@/hooks/stationAdmin/useStationAdmin";
import { AppLayout } from "@/layouts/AppLayout";
import { stationAdminService } from "@/services/stationAdminService";
import { getStoredStation } from "@/stores/authStore";
import type {
  CreateOfficerRequest,
  OfficerMutationResult,
  StationAdminOfficerItem,
  UpdateOfficerRequest,
} from "@/types/api/stationAdmin";

interface CredentialsDialogState {
  officer: StationAdminOfficerItem;
  temporaryPassword: string;
}

const INITIAL_OFFICER_FILTERS = { page: 1, page_size: 20 };

function printOfficerCredentials(officer: StationAdminOfficerItem, temporaryPassword: string, stationName: string) {
  const popup = window.open("", "_blank", "width=720,height=640");
  if (!popup) return;
  popup.document.write(`
    <html>
      <head><title>SentinelANPR Officer Credentials</title></head>
      <body style="font-family: Arial, sans-serif; padding: 24px;">
        <h1>SentinelANPR AI Officer Credentials</h1>
        <p><strong>Name:</strong> ${officer.officer_name}</p>
        <p><strong>Role:</strong> POLICE OFFICER</p>
        <p><strong>Username:</strong> ${officer.username}</p>
        <p><strong>Employee ID:</strong> ${officer.employee_id}</p>
        <p><strong>Badge Number:</strong> ${officer.badge_number}</p>
        <p><strong>Station:</strong> ${stationName}</p>
        <p><strong>Temporary Password:</strong> ${temporaryPassword}</p>
        <hr />
        <p>The officer must change this password during first login.</p>
      </body>
    </html>
  `);
  popup.document.close();
  popup.focus();
  popup.print();
}

export function PoliceOfficersPage() {
  const { data, loading, error, filters, setFilters, refresh } = useStationOfficers();
  const { data: profile } = useStationProfile();
  const stationName = profile?.station_name ?? getStoredStation()?.station_name ?? "Assigned Station";
  const [mode, setMode] = useState<"create" | "edit" | "reset_password" | null>(null);
  const [selectedOfficer, setSelectedOfficer] = useState<StationAdminOfficerItem | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [credentialsDialog, setCredentialsDialog] = useState<CredentialsDialogState | null>(null);

  const officerCount = useMemo(() => data?.pagination.total_items ?? 0, [data]);

  async function handleCreate(payload: CreateOfficerRequest) {
    const result: OfficerMutationResult = await stationAdminService.createOfficer(payload);
    setMode(null);
    setMessage(null);
    if (result.temporary_password) {
      setCredentialsDialog({
        officer: result.officer,
        temporaryPassword: result.temporary_password,
      });
    } else {
      setMessage("Officer created successfully.");
    }
    refresh();
  }

  async function handleUpdate(officerId: string, payload: UpdateOfficerRequest) {
    await stationAdminService.updateOfficer(officerId, payload);
    setMessage("Officer updated successfully.");
    setMode(null);
    refresh();
  }

  async function handleReset(officerId: string, password: string) {
    await stationAdminService.resetOfficerPassword(officerId, password);
    setMessage("Password reset successfully.");
    setMode(null);
  }

  async function handleToggle(item: StationAdminOfficerItem) {
    if (!window.confirm(`${item.status === "active" ? "Deactivate" : "Activate"} ${item.officer_name}?`)) return;
    if (item.status === "active") await stationAdminService.deactivateOfficer(item.officer_id);
    else await stationAdminService.activateOfficer(item.officer_id);
    setMessage("Officer status updated.");
    refresh();
  }

  async function handleDelete(item: StationAdminOfficerItem) {
    if (!window.confirm(`Delete ${item.officer_name}? This action cannot be undone.`)) return;
    await stationAdminService.deleteOfficer(item.officer_id);
    setMessage("Officer deleted successfully.");
    refresh();
  }

  return (
    <AppLayout>
      <div className="space-y-6">
        <PageHeader
          badge="Station Administration"
          title="Police Officers"
          description="Manage police officers assigned exclusively to your station."
          actions={
            <Button
              icon={<UserPlus className="h-4 w-4" />}
              onClick={() => {
                setSelectedOfficer(null);
                setMode("create");
              }}
            >
              Create User
            </Button>
          }
        />

        <div className="grid gap-4 sm:grid-cols-3">
          <Card>
            <p className="text-sm text-slate-500">Assigned Station</p>
            <p className="mt-2 text-lg font-semibold text-slate-900">{stationName}</p>
          </Card>
          <Card>
            <p className="text-sm text-slate-500">Station Officers</p>
            <p className="mt-2 text-3xl font-bold text-brand">{officerCount}</p>
          </Card>
          <Card>
            <p className="text-sm text-slate-500">Scope</p>
            <p className="mt-2 text-sm font-medium text-slate-700">Police Officers only · same station</p>
          </Card>
        </div>

        <StationOfficerFiltersBar
          filters={filters}
          onApply={(next) => setFilters({ ...filters, ...next, page: 1 })}
          onReset={() => setFilters({ ...INITIAL_OFFICER_FILTERS })}
        />

        {message && (
          <Alert variant="success" title="Success">
            {message}
          </Alert>
        )}
        {actionError && (
          <Alert variant="error" title="Action Failed">
            {actionError}
          </Alert>
        )}

        {mode && (
          <StationOfficerPanel
            mode={mode}
            officer={selectedOfficer}
            stationName={stationName}
            onClose={() => setMode(null)}
            onCreate={async (payload) => {
              try {
                await handleCreate(payload);
              } catch (err) {
                setActionError(err instanceof Error ? err.message : "Create failed");
              }
            }}
            onUpdate={async (officerId, payload) => {
              try {
                await handleUpdate(officerId, payload);
              } catch (err) {
                setActionError(err instanceof Error ? err.message : "Update failed");
              }
            }}
            onResetPassword={async (officerId, password) => {
              try {
                await handleReset(officerId, password);
              } catch (err) {
                setActionError(err instanceof Error ? err.message : "Reset failed");
              }
            }}
          />
        )}

        {credentialsDialog && (
          <Card title="User Created Successfully">
            <div className="space-y-4">
              <p className="text-sm text-slate-600">
                Share these credentials securely with the officer. They must change the password on first login.
              </p>
              <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm">
                <p>
                  <span className="font-medium text-slate-700">Officer:</span> {credentialsDialog.officer.officer_name}
                </p>
                <p>
                  <span className="font-medium text-slate-700">Username:</span> {credentialsDialog.officer.username}
                </p>
                <p>
                  <span className="font-medium text-slate-700">Temporary Password:</span>{" "}
                  <span className="font-mono">{credentialsDialog.temporaryPassword}</span>
                </p>
              </div>
              <p className="text-xs text-slate-500">
                The officer must change this password during first login.
              </p>
              <div className="flex flex-wrap gap-2">
                <Button
                  variant="secondary"
                  icon={<Copy className="h-4 w-4" />}
                  onClick={() => void navigator.clipboard.writeText(credentialsDialog.temporaryPassword)}
                >
                  Copy Password
                </Button>
                <Button
                  variant="secondary"
                  icon={<Printer className="h-4 w-4" />}
                  onClick={() =>
                    printOfficerCredentials(
                      credentialsDialog.officer,
                      credentialsDialog.temporaryPassword,
                      stationName,
                    )
                  }
                >
                  Print Credentials
                </Button>
                <Button variant="secondary" onClick={() => setCredentialsDialog(null)}>
                  Close
                </Button>
              </div>
            </div>
          </Card>
        )}

        {loading && <LoadingState label="Loading officers..." fullHeight />}
        {error && !loading && (
          <Alert variant="warning" title="Unable to Load Officers">
            {error}
          </Alert>
        )}
        {data && !loading && (
          <StationOfficersTable
            items={data.items}
            onEdit={(item) => {
              setSelectedOfficer(item);
              setMode("edit");
            }}
            onResetPassword={(item) => {
              setSelectedOfficer(item);
              setMode("reset_password");
            }}
            onToggleStatus={(item) => void handleToggle(item).catch((err) => setActionError(err instanceof Error ? err.message : "Status update failed"))}
            onDelete={(item) => void handleDelete(item).catch((err) => setActionError(err instanceof Error ? err.message : "Delete failed"))}
          />
        )}
      </div>
    </AppLayout>
  );
}
