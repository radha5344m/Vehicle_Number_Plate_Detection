import { Filter, RotateCcw } from "lucide-react";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import {
  buildUserFiltersFromDraft,
  filtersToDraft,
  validateDateRange,
  type UserFiltersDraft,
} from "@/lib/userFilters";
import type { UserFilters, UserRole, UserStatus } from "@/types/api/users";

const selectClass =
  "w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 shadow-sm outline-none transition-all duration-200 hover:border-slate-400 focus:border-brand focus:ring-2 focus:ring-blue-500/20";

const roles: Array<{ value: "" | UserRole; label: string }> = [
  { value: "", label: "All roles" },
  { value: "SUPER_ADMIN", label: "Super Admin" },
  { value: "STATION_ADMIN", label: "Station Admin" },
  { value: "POLICE_OFFICER", label: "Police Officer" },
];

const statuses: Array<{ value: "" | UserStatus; label: string }> = [
  { value: "", label: "All statuses" },
  { value: "active", label: "Active" },
  { value: "inactive", label: "Inactive" },
  { value: "suspended", label: "Suspended" },
];

interface Props {
  filters: UserFilters;
  onApply: (filters: UserFilters) => void;
  onReset: () => void;
}

export function UsersFiltersBar({ filters, onApply, onReset }: Props) {
  const [draft, setDraft] = useState<UserFiltersDraft>(() => filtersToDraft(filters));
  const [dateError, setDateError] = useState<string | null>(null);

  useEffect(() => {
    setDraft(filtersToDraft(filters));
    setDateError(null);
  }, [filters]);

  function updateDraft<K extends keyof UserFiltersDraft>(key: K, value: UserFiltersDraft[K]) {
    setDraft((current) => ({ ...current, [key]: value }));
    if (key === "created_from" || key === "created_to") {
      setDateError(null);
    }
  }

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const rangeError = validateDateRange(draft.created_from, draft.created_to);
    if (rangeError) {
      setDateError(rangeError);
      return;
    }
    setDateError(null);
    onApply(
      buildUserFiltersFromDraft(draft, {
        page_size: filters.page_size,
        sort_by: filters.sort_by,
        sort_desc: filters.sort_desc,
      }),
    );
  }

  function handleReset() {
    setDateError(null);
    onReset();
  }

  return (
    <form onSubmit={handleSubmit} className="grid gap-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-soft md:grid-cols-2 xl:grid-cols-4">
      <Input
        name="search"
        label="Search"
        value={draft.search}
        onChange={(event) => updateDraft("search", event.target.value)}
        placeholder="Name, username, employee ID, badge"
      />
      <label className="block text-sm">
        <span className="mb-1.5 block font-medium text-slate-700">Role</span>
        <select
          name="role"
          value={draft.role}
          onChange={(event) => updateDraft("role", event.target.value)}
          className={selectClass}
        >
          {roles.map((role) => <option key={role.value || "all"} value={role.value}>{role.label}</option>)}
        </select>
      </label>
      <Input
        name="station"
        label="Police Station"
        value={draft.station}
        onChange={(event) => updateDraft("station", event.target.value)}
      />
      <label className="block text-sm">
        <span className="mb-1.5 block font-medium text-slate-700">Status</span>
        <select
          name="status"
          value={draft.status}
          onChange={(event) => updateDraft("status", event.target.value)}
          className={selectClass}
        >
          {statuses.map((status) => <option key={status.value || "all"} value={status.value}>{status.label}</option>)}
        </select>
      </label>
      <Input
        type="date"
        name="created_from"
        label="Date Created From"
        value={draft.created_from}
        onChange={(event) => updateDraft("created_from", event.target.value)}
      />
      <Input
        type="date"
        name="created_to"
        label="Date Created To"
        value={draft.created_to}
        onChange={(event) => updateDraft("created_to", event.target.value)}
      />
      {dateError && <p className="text-sm text-red-600 xl:col-span-4">{dateError}</p>}
      <div className="flex items-end gap-2 xl:col-span-2">
        <Button type="submit" icon={<Filter className="h-4 w-4" />}>Apply</Button>
        <Button type="button" variant="secondary" icon={<RotateCcw className="h-4 w-4" />} onClick={handleReset}>
          Reset
        </Button>
      </div>
    </form>
  );
}
