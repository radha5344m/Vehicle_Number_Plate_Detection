import { ChevronLeft, ChevronRight, UserPlus } from "lucide-react";
import { useState } from "react";

import { UsersFiltersBar } from "@/components/features/users/UsersFiltersBar";
import { UserManagementPanel } from "@/components/features/users/UserManagementPanel";
import { UsersTable } from "@/components/features/users/UsersTable";
import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { LoadingState } from "@/components/ui/LoadingState";
import { PageHeader } from "@/components/ui/PageHeader";
import { useUsers } from "@/hooks/users/useUsers";
import { AppLayout } from "@/layouts/AppLayout";
import { hasPermission, hasRole } from "@/lib/rbac";
import { usersService } from "@/services/usersService";
import type { CreateUserRequest, UpdateUserRequest, UserItem } from "@/types/api/users";

const INITIAL_FILTERS = {
  page: 1,
  page_size: 20,
  sort_by: "created_at",
  sort_desc: true,
} as const;

export function UsersPage() {
  const isSuperAdmin = hasRole("SUPER_ADMIN");
  const canManageUsers = hasPermission("users");
  const { data, loading, error, filters, setFilters, setPage, refresh } = useUsers(INITIAL_FILTERS);
  const [panelMode, setPanelMode] = useState<"create" | "edit" | "reset_password" | null>(null);
  const [selectedUser, setSelectedUser] = useState<UserItem | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);

  if (!isSuperAdmin) {
    return (
      <AppLayout>
        <Alert variant="warning" title="Access Denied">Only SUPER_ADMIN can access User Management.</Alert>
      </AppLayout>
    );
  }

  async function handleCreate(payload: CreateUserRequest) {
    setActionError(null);
    await usersService.create(payload);
    setActionSuccess("User created successfully.");
    setPanelMode(null);
    refresh();
  }

  async function handleUpdate(officerId: string, payload: UpdateUserRequest) {
    setActionError(null);
    await usersService.update(officerId, payload);
    setActionSuccess("User updated successfully.");
    setPanelMode(null);
    refresh();
  }

  async function handleResetPassword(officerId: string, newPassword: string) {
    setActionError(null);
    await usersService.resetPassword(officerId, { new_password: newPassword });
    setActionSuccess("Password reset successfully.");
    setPanelMode(null);
  }

  async function handleToggleStatus(user: UserItem) {
    if (!window.confirm(`${user.status === "active" ? "Deactivate" : "Activate"} ${user.full_name}?`)) return;
    if (user.status === "active") {
      await usersService.deactivate(user.officer_id);
      setActionSuccess("User deactivated successfully.");
    } else {
      await usersService.activate(user.officer_id);
      setActionSuccess("User activated successfully.");
    }
    refresh();
  }

  async function handleDelete(user: UserItem) {
    if (!window.confirm(`Soft delete ${user.full_name}?`)) return;
    await usersService.delete(user.officer_id);
    setActionSuccess("User deleted successfully.");
    refresh();
  }

  return (
    <AppLayout>
      <div className="space-y-6">
        <PageHeader
          badge="Administration"
          title="Users"
          description="Manage station administrators and police officers with enterprise search, filters, status controls, and password reset actions."
          actions={
            canManageUsers ? (
              <Button icon={<UserPlus className="h-4 w-4" />} onClick={() => { setSelectedUser(null); setPanelMode("create"); }}>
                Create User
              </Button>
            ) : undefined
          }
        />

        <UsersFiltersBar filters={filters} onApply={(next) => setFilters(next)} onReset={() => setFilters({ ...INITIAL_FILTERS })} />

        {actionSuccess && <Alert variant="success" title="Success">{actionSuccess}</Alert>}
        {actionError && <Alert variant="error" title="Action Failed">{actionError}</Alert>}

        {panelMode && (
          <UserManagementPanel
            mode={panelMode}
            user={selectedUser}
            onClose={() => setPanelMode(null)}
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
            onResetPassword={async (officerId, newPassword) => {
              try {
                await handleResetPassword(officerId, newPassword);
              } catch (err) {
                setActionError(err instanceof Error ? err.message : "Reset password failed");
              }
            }}
          />
        )}

        {loading && <LoadingState label="Loading users..." fullHeight />}
        {error && !loading && <Alert variant="warning" title="Unable to Load Users">{error}</Alert>}

        {data && !loading && (
          <div className="space-y-4">
            <p className="text-sm text-slate-500">Showing {data.items.length} of {data.pagination.total_items} users</p>
            <UsersTable
              items={data.items}
              onEdit={(user) => { setSelectedUser(user); setPanelMode("edit"); }}
              onResetPassword={(user) => { setSelectedUser(user); setPanelMode("reset_password"); }}
              onToggleStatus={(user) => void handleToggleStatus(user)}
              onDelete={(user) => void handleDelete(user)}
              canManage={canManageUsers}
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
