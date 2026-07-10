import { Building2, UserPlus, Users } from "lucide-react";
import { useMemo, useState } from "react";

import { StationManagementPanel } from "@/components/features/stations/StationManagementPanel";
import { StationsFiltersBar } from "@/components/features/stations/StationsFiltersBar";
import { StationsTable } from "@/components/features/stations/StationsTable";
import { UserCredentialsSuccessDialog } from "@/components/features/users/UserCredentialsSuccessDialog";
import { UserManagementPanel } from "@/components/features/users/UserManagementPanel";
import { UsersFiltersBar } from "@/components/features/users/UsersFiltersBar";
import { UsersTable } from "@/components/features/users/UsersTable";
import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { LoadingState } from "@/components/ui/LoadingState";
import { PageHeader } from "@/components/ui/PageHeader";
import { useStations } from "@/hooks/stations/useStations";
import { useUsers } from "@/hooks/users/useUsers";
import { AppLayout } from "@/layouts/AppLayout";
import { hasPermission, hasRole } from "@/lib/rbac";
import { userFromUserItem } from "@/lib/userCredentials";
import { stationsService } from "@/services/stationsService";
import { usersService } from "@/services/usersService";
import type { CreateStationRequest, StationItem, UpdateStationRequest } from "@/types/api/stations";
import type {
  CreateUserRequest,
  UpdateUserRequest,
  UserItem,
  UserMutationResult,
  UserRole,
} from "@/types/api/users";

const USER_FILTERS = {
  page: 1,
  page_size: 20,
  sort_by: "created_at",
  sort_desc: true,
} as const;

const STATION_FILTERS = {
  page: 1,
  page_size: 20,
  sort_by: "created_at",
  sort_desc: true,
} as const;

type TabKey = "users" | "stations";

type UserDialogStep = "role" | "form";

interface PendingStationAssignment {
  payload: CreateStationRequest;
  stationAdminOfficerId: string;
  policeOfficerIds: string[];
}

interface CredentialsDialogState {
  user: UserMutationResult["user"];
  temporaryPassword: string;
  mode: "create" | "reset";
}

function splitFullName(fullName: string): { firstName: string; lastName: string } {
  const parts = fullName.trim().split(/\s+/).filter(Boolean);
  return {
    firstName: parts[0] ?? "",
    lastName: parts.slice(1).join(" "),
  };
}

export function ManagementPage() {
  const [activeTab, setActiveTab] = useState<TabKey>("users");
  const [userMode, setUserMode] = useState<"create" | "edit" | null>(null);
  const [userDialogStep, setUserDialogStep] = useState<UserDialogStep>("role");
  const [createRole, setCreateRole] = useState<UserRole | null>(null);
  const [selectedUser, setSelectedUser] = useState<UserItem | null>(null);
  const [selectedStation, setSelectedStation] = useState<StationItem | null>(null);
  const [stationMode, setStationMode] = useState<"create" | "edit" | null>(null);
  const [pendingStationAssignment, setPendingStationAssignment] = useState<PendingStationAssignment | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);
  const [credentialsDialog, setCredentialsDialog] = useState<CredentialsDialogState | null>(null);

  const canManageUsers = hasPermission("users");
  const canManageStations = hasPermission("stations");
  const isSuperAdmin = hasRole("SUPER_ADMIN");

  const users = useUsers(USER_FILTERS, isSuperAdmin);
  const stations = useStations(STATION_FILTERS);

  const stationOptions = useMemo(
    () => (stations.data?.items ?? []).map((station) => station.station_name),
    [stations.data],
  );
  const stationAdminOptions = useMemo(
    () =>
      (users.data?.items ?? [])
        .filter((item) => item.role === "STATION_ADMIN")
        .map((item) => ({ officer_id: item.officer_id, full_name: item.full_name })),
    [users.data],
  );
  const assignableStationAdmins = useMemo(
    () => (users.data?.items ?? []).filter((item) => item.role === "STATION_ADMIN"),
    [users.data],
  );
  const assignablePoliceOfficers = useMemo(
    () => (users.data?.items ?? []).filter((item) => item.role === "POLICE_OFFICER"),
    [users.data],
  );

  if (!isSuperAdmin) {
    return (
      <AppLayout>
        <Alert variant="warning" title="Access Denied">
          Only SUPER_ADMIN can access Management.
        </Alert>
      </AppLayout>
    );
  }

  async function handleCreateUser(payload: CreateUserRequest) {
    const result = await usersService.create(payload);
    users.refresh();
    setUserMode(null);
    setCreateRole(null);
    setUserDialogStep("role");
    setActionSuccess(null);
    if (result.temporary_password) {
      setCredentialsDialog({
        user: result.user,
        temporaryPassword: result.temporary_password,
        mode: "create",
      });
    }
  }

  async function handleUpdateUser(officerId: string, payload: UpdateUserRequest) {
    await usersService.update(officerId, payload);
    users.refresh();
    setUserMode(null);
    setActionSuccess("User updated successfully.");
  }

  async function handleAdminResetPassword(user: UserItem) {
    if (
      !window.confirm(
        `Generate a new temporary password for ${user.full_name}? The previous password will stop working immediately.`,
      )
    ) {
      return;
    }
    const result = await usersService.resetPassword(user.officer_id);
    users.refresh();
    setUserMode(null);
    setSelectedUser(null);
    setActionSuccess(null);
    if (result.temporary_password) {
      setCredentialsDialog({
        user: result.user,
        temporaryPassword: result.temporary_password,
        mode: "reset",
      });
    }
  }

  async function handleToggleUser(user: UserItem) {
    if (!window.confirm(`${user.status === "active" ? "Deactivate" : "Activate"} ${user.full_name}?`)) return;
    if (user.status === "active") {
      await usersService.deactivate(user.officer_id);
      setActionSuccess("User deactivated successfully.");
    } else {
      await usersService.activate(user.officer_id);
      setActionSuccess("User activated successfully.");
    }
    users.refresh();
  }

  async function handleDeleteUser(user: UserItem) {
    if (!window.confirm(`Soft delete ${user.full_name}?`)) return;
    await usersService.delete(user.officer_id);
    setActionSuccess("User deleted successfully.");
    users.refresh();
  }

  async function handleCreateStation(payload: CreateStationRequest) {
    setPendingStationAssignment({
      payload,
      stationAdminOfficerId: "",
      policeOfficerIds: [],
    });
  }

  async function handleUpdateStation(stationId: string, payload: UpdateStationRequest) {
    await stationsService.update(stationId, payload);
    stations.refresh();
    setStationMode(null);
    setActionSuccess("Station updated successfully.");
  }

  async function handleToggleStation(station: StationItem) {
    if (!window.confirm(`${station.status === "active" ? "Deactivate" : "Activate"} ${station.station_name}?`)) return;
    await stationsService.changeStatus(station.station_id, station.status === "active" ? "inactive" : "active");
    setActionSuccess(`Station ${station.status === "active" ? "deactivated" : "activated"} successfully.`);
    stations.refresh();
  }

  async function handleDeleteStation(station: StationItem) {
    if (!window.confirm(`Soft delete ${station.station_name}?`)) return;
    await stationsService.delete(station.station_id);
    setActionSuccess("Station deleted successfully.");
    stations.refresh();
  }

  const stationStats = useMemo(() => {
    const items = stations.data?.items ?? [];
    return {
      total: stations.data?.pagination.total_items ?? 0,
      active: items.filter((item) => item.status === "active").length,
      inactive: items.filter((item) => item.status === "inactive").length,
      districts: new Set(items.map((item) => item.district)).size,
    };
  }, [stations.data]);

  async function finalizeStationCreation() {
    if (!pendingStationAssignment) return;
    const result = await stationsService.create(pendingStationAssignment.payload);
    const newStationName = result.station.station_name;
    const district = result.station.district;
    const selectedIds = [
      pendingStationAssignment.stationAdminOfficerId,
      ...pendingStationAssignment.policeOfficerIds,
    ].filter(Boolean);
    for (const officerId of selectedIds) {
      const user = users.data?.items.find((item) => item.officer_id === officerId);
      if (!user) continue;
      const names = splitFullName(user.full_name);
      await usersService.update(officerId, {
        employee_id: user.employee_id,
        first_name: names.firstName,
        last_name: names.lastName,
        email: user.email,
        phone_number: user.phone_number ?? undefined,
        rank: user.rank,
        role: user.role,
        police_station: newStationName,
        district,
        status: user.status,
      });
    }
    stations.refresh();
    users.refresh();
    setPendingStationAssignment(null);
    setStationMode(null);
    setActionSuccess("Station created successfully.");
  }

  return (
    <AppLayout>
      <div className="space-y-6">
        <PageHeader
          badge="Administration"
          title="Management"
          description="Unified management for police stations and system users with secure credential handling."
          actions={
            activeTab === "users" && canManageUsers ? (
              <Button
                icon={<UserPlus className="h-4 w-4" />}
                onClick={() => {
                  setSelectedUser(null);
                  setUserMode("create");
                  setUserDialogStep("role");
                  setCreateRole(null);
                }}
              >
                Create User
              </Button>
            ) : activeTab === "stations" && canManageStations ? (
              <Button
                icon={<Building2 className="h-4 w-4" />}
                onClick={() => {
                  setSelectedStation(null);
                  setStationMode("create");
                }}
              >
                Create Station
              </Button>
            ) : undefined
          }
        />

        <div className="flex flex-wrap gap-3">
          <Button
            variant={activeTab === "users" ? "primary" : "secondary"}
            onClick={() => setActiveTab("users")}
            icon={<Users className="h-4 w-4" />}
          >
            Users
          </Button>
          <Button
            variant={activeTab === "stations" ? "primary" : "secondary"}
            onClick={() => setActiveTab("stations")}
            icon={<Building2 className="h-4 w-4" />}
          >
            Police Stations
          </Button>
        </div>

        {actionSuccess && (
          <Alert variant="success" title="Success">
            {actionSuccess}
          </Alert>
        )}
        {actionError && (
          <Alert variant="error" title="Action Failed">
            {actionError}
          </Alert>
        )}

        {credentialsDialog && (
          <UserCredentialsSuccessDialog
            user={userFromUserItem(credentialsDialog.user)}
            temporaryPassword={credentialsDialog.temporaryPassword}
            mode={credentialsDialog.mode}
            onClose={() => setCredentialsDialog(null)}
          />
        )}

        {activeTab === "stations" && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
              <Card>
                <p className="text-sm text-slate-500">Total Stations</p>
                <p className="mt-2 text-3xl font-bold text-slate-900">{stationStats.total}</p>
              </Card>
              <Card>
                <p className="text-sm text-slate-500">Active</p>
                <p className="mt-2 text-3xl font-bold text-slate-900">{stationStats.active}</p>
              </Card>
              <Card>
                <p className="text-sm text-slate-500">Inactive</p>
                <p className="mt-2 text-3xl font-bold text-slate-900">{stationStats.inactive}</p>
              </Card>
              <Card>
                <p className="text-sm text-slate-500">Districts</p>
                <p className="mt-2 text-3xl font-bold text-slate-900">{stationStats.districts}</p>
              </Card>
            </div>

            <StationsFiltersBar
              filters={stations.filters}
              onApply={(next) => stations.setFilters(next)}
              onReset={() => stations.setFilters({ ...STATION_FILTERS })}
            />

            {stationMode && (
              <div className="space-y-4">
                {!pendingStationAssignment && (
                  <StationManagementPanel
                    mode={stationMode}
                    station={selectedStation}
                    onClose={() => setStationMode(null)}
                    onCreate={async (payload) => {
                      try {
                        await handleCreateStation(payload);
                      } catch (err) {
                        setActionError(err instanceof Error ? err.message : "Create failed");
                      }
                    }}
                    onUpdate={async (stationId, payload) => {
                      try {
                        await handleUpdateStation(stationId, payload);
                      } catch (err) {
                        setActionError(err instanceof Error ? err.message : "Update failed");
                      }
                    }}
                  />
                )}
                {pendingStationAssignment && (
                  <Card
                    title="Optional User Assignment"
                    description="Assign existing station admins and police officers before completing station creation."
                    icon={<Users className="h-4 w-4" />}
                  >
                    <div className="grid gap-4 md:grid-cols-2">
                      <label className="block text-sm">
                        <span className="mb-1.5 block font-medium text-slate-700">Existing Station Admin</span>
                        <select
                          className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm"
                          value={pendingStationAssignment.stationAdminOfficerId}
                          onChange={(event) =>
                            setPendingStationAssignment((current) =>
                              current
                                ? { ...current, stationAdminOfficerId: event.target.value }
                                : current,
                            )
                          }
                        >
                          <option value="">No assignment</option>
                          {assignableStationAdmins.map((item) => (
                            <option key={item.officer_id} value={item.officer_id}>
                              {item.full_name}
                            </option>
                          ))}
                        </select>
                      </label>
                      <label className="block text-sm">
                        <span className="mb-1.5 block font-medium text-slate-700">Existing Police Officers</span>
                        <select
                          multiple
                          className="min-h-[140px] w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm"
                          value={pendingStationAssignment.policeOfficerIds}
                          onChange={(event) =>
                            setPendingStationAssignment((current) =>
                              current
                                ? {
                                    ...current,
                                    policeOfficerIds: Array.from(event.target.selectedOptions).map(
                                      (option) => option.value,
                                    ),
                                  }
                                : current,
                            )
                          }
                        >
                          {assignablePoliceOfficers.map((item) => (
                            <option key={item.officer_id} value={item.officer_id}>
                              {item.full_name}
                            </option>
                          ))}
                        </select>
                      </label>
                    </div>
                    <div className="mt-4 flex flex-wrap gap-2">
                      <Button onClick={() => void finalizeStationCreation()}>Finish Station Creation</Button>
                      <Button
                        variant="secondary"
                        onClick={() => {
                          setPendingStationAssignment(null);
                          setStationMode(null);
                        }}
                      >
                        Cancel
                      </Button>
                    </div>
                  </Card>
                )}
              </div>
            )}

            {stations.loading && <LoadingState label="Loading stations..." fullHeight />}
            {stations.error && !stations.loading && (
              <Alert variant="warning" title="Unable to Load Stations">
                {stations.error}
              </Alert>
            )}
            {stations.data && !stations.loading && (
              <StationsTable
                items={stations.data.items}
                onEdit={(station) => {
                  setSelectedStation(station);
                  setStationMode("edit");
                }}
                onToggleStatus={(station) => void handleToggleStation(station)}
                onDelete={(station) => void handleDeleteStation(station)}
                canManage={canManageStations}
              />
            )}
          </div>
        )}

        {activeTab === "users" && (
          <div className="space-y-6">
            {users.data && (
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
                <Card>
                  <p className="text-sm text-slate-500">Total Users</p>
                  <p className="mt-2 text-3xl font-bold text-slate-900">{users.data.summary.total_users}</p>
                </Card>
                <Card>
                  <p className="text-sm text-slate-500">Super Admins</p>
                  <p className="mt-2 text-3xl font-bold text-slate-900">{users.data.summary.super_admins}</p>
                </Card>
                <Card>
                  <p className="text-sm text-slate-500">Station Admins</p>
                  <p className="mt-2 text-3xl font-bold text-slate-900">{users.data.summary.station_admins}</p>
                </Card>
                <Card>
                  <p className="text-sm text-slate-500">Police Officers</p>
                  <p className="mt-2 text-3xl font-bold text-slate-900">{users.data.summary.police_officers}</p>
                </Card>
              </div>
            )}
            <UsersFiltersBar
              filters={users.filters}
              onApply={(next) => users.setFilters(next)}
              onReset={() => users.setFilters({ ...USER_FILTERS })}
            />

            {userMode === "create" && userDialogStep === "role" && (
              <Card
                title="What role do you want to create?"
                description="Choose the role first, then complete the appropriate user form."
                icon={<UserPlus className="h-4 w-4" />}
              >
                <div className="grid gap-3 md:grid-cols-3">
                  {(["SUPER_ADMIN", "STATION_ADMIN", "POLICE_OFFICER"] as UserRole[]).map((role) => (
                    <button
                      key={role}
                      type="button"
                      className={`rounded-2xl border p-5 text-left transition ${
                        createRole === role
                          ? "border-blue-300 bg-blue-50"
                          : "border-slate-200 bg-white hover:border-slate-300"
                      }`}
                      onClick={() => setCreateRole(role)}
                    >
                      <p className="font-semibold text-slate-900">{role.replaceAll("_", " ")}</p>
                    </button>
                  ))}
                </div>
                <div className="mt-4 flex gap-2">
                  <Button
                    onClick={() => {
                      if (!createRole) return;
                      setUserDialogStep("form");
                    }}
                    disabled={!createRole}
                  >
                    Continue
                  </Button>
                  <Button
                    variant="secondary"
                    onClick={() => {
                      setUserMode(null);
                      setCreateRole(null);
                    }}
                  >
                    Cancel
                  </Button>
                </div>
              </Card>
            )}

            {((userMode === "create" && userDialogStep === "form") || userMode === "edit") && (
              <UserManagementPanel
                mode={userMode}
                user={selectedUser}
                createRole={userMode === "create" ? createRole : null}
                stationOptions={stationOptions}
                reportingStationAdminOptions={stationAdminOptions}
                onClose={() => {
                  setUserMode(null);
                  setCreateRole(null);
                  setUserDialogStep("role");
                }}
                onCreate={async (payload) => {
                  try {
                    await handleCreateUser(payload);
                  } catch (err) {
                    setActionError(err instanceof Error ? err.message : "Create failed");
                  }
                }}
                onUpdate={async (officerId, payload) => {
                  try {
                    await handleUpdateUser(officerId, payload);
                  } catch (err) {
                    setActionError(err instanceof Error ? err.message : "Update failed");
                  }
                }}
              />
            )}

            {users.loading && <LoadingState label="Loading users..." fullHeight />}
            {users.error && !users.loading && (
              <Alert variant="warning" title="Unable to Load Users">
                {users.error}
              </Alert>
            )}
            {users.data && !users.loading && (
              <UsersTable
                items={users.data.items}
                onEdit={(user) => {
                  setSelectedUser(user);
                  setUserMode("edit");
                }}
                onResetPassword={(user) => {
                  void handleAdminResetPassword(user).catch((err) => {
                    setActionError(err instanceof Error ? err.message : "Reset password failed");
                  });
                }}
                onToggleStatus={(user) => void handleToggleUser(user)}
                onDelete={(user) => void handleDeleteUser(user)}
                canManage={canManageUsers}
              />
            )}
          </div>
        )}
      </div>
    </AppLayout>
  );
}
