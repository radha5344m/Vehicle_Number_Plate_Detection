import { Building2, Save, X } from "lucide-react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import type { CreateStationRequest, StationItem, StationStatus, UpdateStationRequest } from "@/types/api/stations";

const selectClass =
  "w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 shadow-sm outline-none transition-all duration-200 hover:border-slate-400 focus:border-brand focus:ring-2 focus:ring-blue-500/20";

interface Props {
  mode: "create" | "edit";
  station: StationItem | null;
  onClose: () => void;
  onCreate: (payload: CreateStationRequest) => Promise<void>;
  onUpdate: (stationId: string, payload: UpdateStationRequest) => Promise<void>;
}

export function StationManagementPanel({ mode, station, onClose, onCreate, onUpdate }: Props) {
  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const payload = {
      station_name: String(form.get("station_name") ?? "").trim(),
      district: String(form.get("district") ?? "").trim(),
      state: String(form.get("state") ?? "").trim(),
      address: String(form.get("address") ?? "").trim(),
      pincode: String(form.get("pincode") ?? "").trim(),
      phone_number: String(form.get("phone_number") ?? "").trim() || undefined,
      email: String(form.get("email") ?? "").trim() || undefined,
      station_type: String(form.get("station_type") ?? "").trim(),
      status: String(form.get("status") ?? "") as StationStatus,
    };

    if (mode === "create") {
      await onCreate({
        ...payload,
        station_code: String(form.get("station_code") ?? "").trim(),
      });
      return;
    }

    if (station) {
      await onUpdate(station.station_id, payload);
    }
  }

  return (
    <Card
      title={mode === "create" ? "Create Police Station" : `Edit ${station?.station_name ?? "Station"}`}
      icon={<Building2 className="h-4 w-4" />}
      className="print:hidden"
    >
      <form onSubmit={(event) => void handleSubmit(event)} className="grid gap-4 md:grid-cols-2">
        {mode === "create" && <Input name="station_code" label="Station Code" required defaultValue={station?.station_code ?? ""} />}
        <Input name="station_name" label="Station Name" required defaultValue={station?.station_name ?? ""} />
        <Input name="district" label="District" required defaultValue={station?.district ?? ""} />
        <Input name="state" label="State" required defaultValue={station?.state ?? ""} />
        <Input name="pincode" label="Pincode" required defaultValue={station?.pincode ?? ""} />
        <Input name="phone_number" label="Phone Number" defaultValue={station?.phone_number ?? ""} />
        <Input name="email" label="Email" type="email" defaultValue={station?.email ?? ""} />
        <Input name="station_type" label="Station Type" required defaultValue={station?.station_type ?? ""} />
        <label className="block text-sm">
          <span className="mb-1.5 block font-medium text-slate-700">Status</span>
          <select name="status" className={selectClass} defaultValue={station?.status ?? "active"}>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </select>
        </label>
        <div className="md:col-span-2">
          <Input name="address" label="Address" required defaultValue={station?.address ?? ""} />
        </div>
        <div className="flex gap-2 md:col-span-2">
          <Button type="submit" icon={<Save className="h-4 w-4" />}>{mode === "create" ? "Create Station" : "Save Changes"}</Button>
          <Button type="button" variant="secondary" icon={<X className="h-4 w-4" />} onClick={onClose}>Cancel</Button>
        </div>
      </form>
    </Card>
  );
}
