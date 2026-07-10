import { Filter, RotateCcw } from "lucide-react";
import { useEffect, useState } from "react";

import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import type { CreateOfficerRequest, StationAdminOfficerItem, UpdateOfficerRequest } from "@/types/api/stationAdmin";

interface StationOfficerFiltersDraft {
  search: string;
  rank: string;
  status: string;
}

function stationOfficerFiltersToDraft(filters: {
  search?: string;
  status?: string;
  rank?: string;
}): StationOfficerFiltersDraft {
  return {
    search: filters.search ?? "",
    rank: filters.rank ?? "",
    status: filters.status ?? "",
  };
}

function splitFullName(fullName: string): { firstName: string; lastName: string } {
  const parts = fullName.trim().split(/\s+/).filter(Boolean);
  return {
    firstName: parts[0] ?? "",
    lastName: parts.slice(1).join(" ") || parts[0] || "",
  };
}

export function StationOfficerFiltersBar({
  filters,
  onApply,
  onReset,
}: {
  filters: { search?: string; status?: string; rank?: string };
  onApply: (filters: { search?: string; status?: string; rank?: string }) => void;
  onReset: () => void;
}) {
  const [draft, setDraft] = useState<StationOfficerFiltersDraft>(() =>
    stationOfficerFiltersToDraft(filters),
  );

  useEffect(() => {
    setDraft(stationOfficerFiltersToDraft(filters));
  }, [filters]);

  function updateDraft<K extends keyof StationOfficerFiltersDraft>(
    key: K,
    value: StationOfficerFiltersDraft[K],
  ) {
    setDraft((current) => ({ ...current, [key]: value }));
  }

  return (
    <form
      className="grid gap-4 rounded-2xl border border-slate-200 bg-white p-4 shadow-soft sm:p-5 md:grid-cols-2 xl:grid-cols-4"
      onSubmit={(event) => {
        event.preventDefault();
        onApply({
          search: draft.search.trim() || undefined,
          status: draft.status.trim() || undefined,
          rank: draft.rank.trim() || undefined,
        });
      }}
    >
      <Input
        name="search"
        label="Search"
        value={draft.search}
        onChange={(event) => updateDraft("search", event.target.value)}
        placeholder="Employee, badge, officer"
      />
      <Input
        name="rank"
        label="Rank"
        value={draft.rank}
        onChange={(event) => updateDraft("rank", event.target.value)}
      />
      <label className="block text-sm">
        <span className="mb-1.5 block font-medium text-slate-700">Status</span>
        <select
          name="status"
          value={draft.status}
          onChange={(event) => updateDraft("status", event.target.value)}
          className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm"
        >
          <option value="">All</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
        </select>
      </label>
      <div className="flex items-end gap-2">
        <Button type="submit" icon={<Filter className="h-4 w-4" />}>
          Apply
        </Button>
        <Button type="button" variant="secondary" icon={<RotateCcw className="h-4 w-4" />} onClick={onReset}>
          Reset
        </Button>
      </div>
    </form>
  );
}

export function StationOfficersTable({
  items,
  onEdit,
  onResetPassword,
  onToggleStatus,
  onDelete,
}: {
  items: StationAdminOfficerItem[];
  onEdit: (item: StationAdminOfficerItem) => void;
  onResetPassword: (item: StationAdminOfficerItem) => void;
  onToggleStatus: (item: StationAdminOfficerItem) => void;
  onDelete: (item: StationAdminOfficerItem) => void;
}) {
  if (items.length === 0) {
    return (
      <p className="rounded-2xl border border-dashed border-slate-300 bg-white px-4 py-12 text-center text-sm text-slate-400">
        No police officers found for your station.
      </p>
    );
  }

  return (
    <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-soft">
      <div className="table-scroll overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead className="border-b border-slate-200 bg-slate-50 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
            <tr>
              <th className="px-4 py-3.5">Employee ID</th>
              <th className="px-4 py-3.5">Badge</th>
              <th className="px-4 py-3.5">Officer</th>
              <th className="px-4 py-3.5">Rank</th>
              <th className="px-4 py-3.5">Phone</th>
              <th className="px-4 py-3.5">Status</th>
              <th className="px-4 py-3.5">Investigations</th>
              <th className="px-4 py-3.5">Last Login</th>
              <th className="px-4 py-3.5">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {items.map((item) => (
              <tr key={item.officer_id} className="hover:bg-slate-50">
                <td className="px-4 py-3.5 font-mono">{item.employee_id}</td>
                <td className="px-4 py-3.5 font-mono">{item.badge_number}</td>
                <td className="px-4 py-3.5">
                  <div className="font-medium text-slate-900">{item.officer_name}</div>
                  <div className="text-xs text-slate-500">{item.username}</div>
                </td>
                <td className="px-4 py-3.5">{item.rank}</td>
                <td className="px-4 py-3.5">{item.phone_number ?? "-"}</td>
                <td className="px-4 py-3.5">
                  <Badge variant={item.status === "active" ? "success" : "warning"}>{item.status}</Badge>
                </td>
                <td className="px-4 py-3.5">{item.investigations}</td>
                <td className="px-4 py-3.5 text-slate-500">
                  {item.last_login_at ? new Date(item.last_login_at).toLocaleString() : "Never"}
                </td>
                <td className="px-4 py-3.5">
                  <div className="flex flex-wrap gap-2">
                    <Button size="sm" variant="secondary" onClick={() => onEdit(item)}>
                      Edit
                    </Button>
                    <Button size="sm" variant="secondary" onClick={() => onResetPassword(item)}>
                      Reset Password
                    </Button>
                    <Button size="sm" variant="secondary" onClick={() => onToggleStatus(item)}>
                      {item.status === "active" ? "Deactivate" : "Activate"}
                    </Button>
                    <Button size="sm" variant="danger" onClick={() => onDelete(item)}>
                      Delete
                    </Button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export function StationOfficerPanel({
  mode,
  officer,
  stationName,
  onClose,
  onCreate,
  onUpdate,
  onResetPassword,
}: {
  mode: "create" | "edit" | "reset_password";
  officer: StationAdminOfficerItem | null;
  stationName: string;
  onClose: () => void;
  onCreate: (payload: CreateOfficerRequest) => Promise<void>;
  onUpdate: (officerId: string, payload: UpdateOfficerRequest) => Promise<void>;
  onResetPassword: (officerId: string, password: string) => Promise<void>;
}) {
  return (
    <Card
      title={
        mode === "create"
          ? "Create Police Officer"
          : mode === "edit"
            ? `Edit ${officer?.officer_name ?? "Officer"}`
            : `Reset Password for ${officer?.officer_name ?? "Officer"}`
      }
    >
      <form
        className="grid gap-4 md:grid-cols-2"
        onSubmit={(event) => {
          event.preventDefault();
          const form = new FormData(event.currentTarget);
          if (mode === "create") {
            const { firstName, lastName } = splitFullName(String(form.get("full_name") ?? ""));
            void onCreate({
              employee_id: String(form.get("employee_id") ?? "").trim(),
              first_name: firstName,
              last_name: lastName,
              username: String(form.get("username") ?? "").trim(),
              email: String(form.get("email") ?? "").trim(),
              phone_number: String(form.get("phone_number") ?? "").trim() || undefined,
              badge_number: String(form.get("badge_number") ?? "").trim(),
              rank: String(form.get("rank") ?? "").trim(),
              status: String(form.get("status") ?? "active"),
            });
          } else if (mode === "edit" && officer) {
            const names = officer.officer_name.split(" ");
            void onUpdate(officer.officer_id, {
              first_name: String(form.get("first_name") ?? names[0] ?? "").trim(),
              last_name: String(form.get("last_name") ?? names.slice(1).join(" ") ?? "").trim(),
              email: String(form.get("email") ?? "").trim(),
              phone_number: String(form.get("phone_number") ?? "").trim() || undefined,
              rank: String(form.get("rank") ?? "").trim(),
              status: String(form.get("status") ?? "active"),
            });
          } else if (mode === "reset_password" && officer) {
            void onResetPassword(officer.officer_id, String(form.get("password") ?? ""));
          }
        }}
      >
        {mode === "create" && (
          <>
            <div className="md:col-span-2 rounded-xl border border-blue-100 bg-blue-50/60 px-4 py-3 text-sm text-slate-700">
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-medium text-slate-900">Role:</span>
                <Badge variant="info">POLICE OFFICER</Badge>
                <span className="font-medium text-slate-900">Station:</span>
                <span>{stationName}</span>
              </div>
              <p className="mt-2 text-xs text-slate-500">
                Officers are always created for your assigned station. A secure temporary password will be generated
                automatically.
              </p>
            </div>
            <Input name="full_name" label="Full Name" required className="md:col-span-2" />
            <Input name="employee_id" label="Employee ID" required />
            <Input name="username" label="Username" required />
            <Input name="badge_number" label="Badge Number" required />
            <Input name="email" label="Email" type="email" required />
            <Input name="phone_number" label="Phone" />
            <Input name="rank" label="Rank" required />
            <label className="block text-sm">
              <span className="mb-1.5 block font-medium text-slate-700">Status</span>
              <select
                name="status"
                defaultValue="active"
                className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm"
              >
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
              </select>
            </label>
            <Input
              label="Police Station"
              value={stationName}
              readOnly
              disabled
              className="md:col-span-2"
            />
          </>
        )}

        {mode === "edit" && (
          <>
            <Input
              name="first_name"
              label="First Name"
              required
              defaultValue={officer?.officer_name.split(" ")[0] ?? ""}
            />
            <Input
              name="last_name"
              label="Last Name"
              required
              defaultValue={officer?.officer_name.split(" ").slice(1).join(" ") ?? ""}
            />
            <Input name="email" label="Email" required type="email" defaultValue={officer?.email ?? ""} />
            <Input name="phone_number" label="Phone Number" defaultValue={officer?.phone_number ?? ""} />
            <Input name="rank" label="Rank" required defaultValue={officer?.rank ?? ""} />
            <label className="block text-sm">
              <span className="mb-1.5 block font-medium text-slate-700">Status</span>
              <select
                name="status"
                className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm"
                defaultValue={officer?.status ?? "active"}
              >
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
              </select>
            </label>
          </>
        )}

        {mode === "reset_password" && (
          <Input
            name="password"
            label="New Password"
            type="password"
            required
            minLength={8}
            className="md:col-span-2"
          />
        )}

        <div className="flex gap-2 md:col-span-2">
          <Button type="submit">
            {mode === "create" ? "Create Officer" : mode === "edit" ? "Save Changes" : "Reset Password"}
          </Button>
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancel
          </Button>
        </div>
      </form>
    </Card>
  );
}
