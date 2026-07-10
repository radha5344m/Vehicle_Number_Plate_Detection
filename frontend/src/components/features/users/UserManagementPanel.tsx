import { Save, UserPlus, X } from "lucide-react";
import { useMemo, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import type { CreateUserRequest, UpdateUserRequest, UserItem, UserRole, UserStatus } from "@/types/api/users";

const selectClass =
  "w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 shadow-sm outline-none transition-all duration-200 hover:border-slate-400 focus:border-brand focus:ring-2 focus:ring-blue-500/20";

export interface ReportingStationAdminOption {
  officer_id: string;
  full_name: string;
}

interface Props {
  mode: "create" | "edit";
  user: UserItem | null;
  stationOptions?: string[];
  createRole?: UserRole | null;
  reportingStationAdminOptions?: ReportingStationAdminOption[];
  onClose: () => void;
  onCreate: (payload: CreateUserRequest) => Promise<void>;
  onUpdate: (officerId: string, payload: UpdateUserRequest) => Promise<void>;
}

function splitName(fullName: string | undefined): { firstName: string; lastName: string } {
  const parts = (fullName ?? "").trim().split(/\s+/).filter(Boolean);
  const firstName = parts[0] ?? "";
  const lastName = parts.slice(1).join(" ");
  return { firstName, lastName };
}

function resolveCreateRole(
  createRole: UserRole | null,
  selectedRole: UserRole,
  formRole: FormDataEntryValue | null,
): UserRole {
  if (createRole) return createRole;
  if (selectedRole) return selectedRole;
  return String(formRole ?? "") as UserRole;
}

export function UserManagementPanel({
  mode,
  user,
  stationOptions = [],
  createRole = null,
  reportingStationAdminOptions = [],
  onClose,
  onCreate,
  onUpdate,
}: Props) {
  const initialNames = useMemo(() => splitName(user?.full_name), [user?.full_name]);
  const [selectedRole, setSelectedRole] = useState<UserRole>(createRole ?? user?.role ?? "POLICE_OFFICER");
  const stationRequired = selectedRole !== "SUPER_ADMIN";
  const showBadge = selectedRole !== "SUPER_ADMIN";
  const showRank = selectedRole !== "SUPER_ADMIN";
  const showReportingAdmin = selectedRole === "POLICE_OFFICER";
  const [formError, setFormError] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    if (mode === "create") {
      const fullName = String(form.get("full_name") ?? "").trim();
      const names = splitName(fullName);
      const role = resolveCreateRole(createRole, selectedRole, form.get("role"));
      const policeStation = String(form.get("police_station") ?? "").trim() || undefined;

      if (!names.firstName) {
        setFormError("Full name is required.");
        return;
      }
      if (!names.lastName) {
        setFormError("Enter first and last name (e.g. Ravi Kumar).");
        return;
      }
      if (!role) {
        setFormError("Role is required.");
        return;
      }
      if (role !== "SUPER_ADMIN" && !policeStation) {
        setFormError(
          stationOptions.length === 0
            ? "No active stations are available. Create a station first."
            : "Police station is required for Station Admin and Police Officer.",
        );
        return;
      }

      setFormError(null);
      await onCreate({
        first_name: names.firstName,
        last_name: names.lastName,
        email: String(form.get("email") ?? "").trim(),
        phone_number: String(form.get("phone_number") ?? "").trim() || undefined,
        badge_number: String(form.get("badge_number") ?? "").trim() || undefined,
        rank: String(form.get("rank") ?? "").trim() || undefined,
        role,
        police_station: policeStation,
        district: String(form.get("district") ?? "").trim() || undefined,
        status: String(form.get("status") ?? "") as UserStatus,
      });
      return;
    }
    if (mode === "edit" && user) {
      await onUpdate(user.officer_id, {
        employee_id: String(form.get("employee_id") ?? user.employee_id).trim(),
        first_name: String(form.get("first_name") ?? "").trim(),
        last_name: String(form.get("last_name") ?? "").trim(),
        email: String(form.get("email") ?? "").trim(),
        phone_number: String(form.get("phone_number") ?? "").trim() || undefined,
        rank: String(form.get("rank") ?? "").trim(),
        role: (String(form.get("role") ?? "") || undefined) as UserRole | undefined,
        police_station: String(form.get("police_station") ?? "").trim() || undefined,
        district: String(form.get("district") ?? "").trim() || undefined,
        status: String(form.get("status") ?? "") as UserStatus,
      });
      return;
    }
  }

  return (
    <Card
      title={mode === "create" ? "Create User" : `Edit ${user?.full_name ?? "User"}`}
      icon={<UserPlus className="h-4 w-4" />}
      className="print:hidden"
    >
      <form onSubmit={(event) => void handleSubmit(event)} className="grid gap-4 md:grid-cols-2">
        {formError && (
          <p className="text-sm text-red-600 md:col-span-2">{formError}</p>
        )}
        <>
            {mode === "edit" && (
              <Input name="employee_id" label="Employee ID" required defaultValue={user?.employee_id ?? ""} />
            )}
            {mode === "create" ? (
              <Input name="full_name" label="Full Name" required />
            ) : (
              <>
                <Input name="first_name" label="First Name" required defaultValue={initialNames.firstName} />
                <Input name="last_name" label="Last Name" required defaultValue={initialNames.lastName} />
              </>
            )}
            <Input name="email" label="Email" type="email" required defaultValue={user?.email ?? ""} />
            <Input name="phone_number" label="Phone Number" defaultValue={user?.phone_number ?? ""} />
            {mode === "create" && showBadge && (
              <Input name="badge_number" label="Badge Number (optional — defaults to Employee ID)" />
            )}
            {showRank && <Input name="rank" label="Rank" required defaultValue={user?.rank ?? ""} />}
            <label className="block text-sm">
              <span className="mb-1.5 block font-medium text-slate-700">Role</span>
              <select
                name="role"
                className={selectClass}
                defaultValue={selectedRole}
                onChange={(event) => setSelectedRole(event.target.value as UserRole)}
                disabled={mode === "create" && Boolean(createRole)}
              >
                <option value="SUPER_ADMIN">Super Admin</option>
                <option value="STATION_ADMIN">Station Admin</option>
                <option value="POLICE_OFFICER">Police Officer</option>
              </select>
            </label>
            <label className="block text-sm">
              <span className="mb-1.5 block font-medium text-slate-700">
                Police Station {stationRequired ? "" : "(optional for Super Admin)"}
              </span>
              <select
                name="police_station"
                className={selectClass}
                defaultValue={user?.police_station ?? ""}
                required={stationRequired}
                disabled={stationOptions.length === 0}
              >
                <option value="">
                  {stationRequired ? "Select station" : "Headquarters default"}
                </option>
                {stationOptions.map((station) => (
                  <option key={station} value={station}>
                    {station}
                  </option>
                ))}
              </select>
            </label>
            {mode === "create" && showReportingAdmin && (
              <label className="block text-sm">
                <span className="mb-1.5 block font-medium text-slate-700">Reporting Station Admin (Optional)</span>
                <select name="reporting_station_admin" className={selectClass} defaultValue="">
                  <option value="">Not assigned</option>
                  {reportingStationAdminOptions.map((option) => (
                    <option key={option.officer_id} value={option.officer_id}>
                      {option.full_name}
                    </option>
                  ))}
                </select>
              </label>
            )}
            <Input name="district" label="District" defaultValue={user?.district ?? ""} />
            {mode === "create" && (
              <label className="block text-sm">
                <span className="mb-1.5 block font-medium text-slate-700">Status</span>
                <select name="status" className={selectClass} defaultValue="active">
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                  <option value="suspended">Suspended</option>
                </select>
              </label>
            )}
            {mode === "edit" && (
              <label className="block text-sm">
                <span className="mb-1.5 block font-medium text-slate-700">Status</span>
                <select name="status" className={selectClass} defaultValue={user?.status ?? "active"}>
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                  <option value="suspended">Suspended</option>
                </select>
              </label>
            )}
          </>
          <div className="flex gap-2 md:col-span-2">
          <Button type="submit" icon={<Save className="h-4 w-4" />}>{mode === "create" ? "Create User" : "Save Changes"}</Button>
          <Button type="button" variant="secondary" icon={<X className="h-4 w-4" />} onClick={onClose}>Cancel</Button>
        </div>
      </form>
    </Card>
  );
}
