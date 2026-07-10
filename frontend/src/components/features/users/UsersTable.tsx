import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import type { UserItem } from "@/types/api/users";

function statusVariant(status: string): "success" | "warning" | "danger" | "default" {
  if (status === "active") return "success";
  if (status === "inactive") return "warning";
  if (status === "suspended") return "danger";
  return "default";
}

interface Props {
  items: UserItem[];
  onEdit: (user: UserItem) => void;
  onResetPassword: (user: UserItem) => void;
  onToggleStatus: (user: UserItem) => void;
  onDelete: (user: UserItem) => void;
  canManage?: boolean;
}

export function UsersTable({
  items,
  onEdit,
  onResetPassword,
  onToggleStatus,
  onDelete,
  canManage = true,
}: Props) {
  if (items.length === 0) {
    return <p className="rounded-2xl border border-dashed border-slate-300 bg-white px-4 py-12 text-center text-sm text-slate-400">No users match the selected filters.</p>;
  }

  return (
    <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-soft">
      <div className="table-scroll overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead className="border-b border-slate-200 bg-slate-50 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
            <tr>
              <th className="px-4 py-3.5">User ID</th>
              <th className="px-4 py-3.5">Employee ID</th>
              <th className="px-4 py-3.5">Name</th>
              <th className="px-4 py-3.5">Role</th>
              <th className="px-4 py-3.5">Station</th>
              <th className="px-4 py-3.5">Status</th>
              <th className="px-4 py-3.5">Created Date</th>
              <th className="px-4 py-3.5">Last Login</th>
              <th className="px-4 py-3.5">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {items.map((user) => (
              <tr key={user.officer_id} className="text-slate-700 transition-colors hover:bg-slate-50">
                <td className="px-4 py-3.5 font-mono">{user.user_id}</td>
                <td className="px-4 py-3.5 font-mono">{user.employee_id}</td>
                <td className="px-4 py-3.5">
                  <div className="font-medium text-slate-900">{user.full_name}</div>
                  <div className="text-xs text-slate-500">{user.username} � {user.badge_number}</div>
                </td>
                <td className="px-4 py-3.5"><Badge variant="info">{user.role.replaceAll("_", " ")}</Badge></td>
                <td className="px-4 py-3.5">{user.police_station}</td>
                <td className="px-4 py-3.5"><Badge variant={statusVariant(user.status)}>{user.status}</Badge></td>
                <td className="px-4 py-3.5 text-slate-500">{new Date(user.created_at).toLocaleDateString()}</td>
                <td className="px-4 py-3.5 text-slate-500">{user.last_login_at ? new Date(user.last_login_at).toLocaleString() : "Never"}</td>
                <td className="px-4 py-3.5">
                  {canManage ? (
                    <div className="flex flex-wrap gap-2">
                      <Button size="sm" variant="secondary" onClick={() => onEdit(user)}>Edit</Button>
                      <Button size="sm" variant="secondary" onClick={() => onResetPassword(user)}>Reset Password</Button>
                      <Button size="sm" variant="secondary" onClick={() => onToggleStatus(user)}>{user.status === "active" ? "Deactivate" : "Activate"}</Button>
                      <Button size="sm" variant="danger" onClick={() => onDelete(user)}>Delete</Button>
                    </div>
                  ) : (
                    <span className="text-xs text-slate-400">No actions available</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
