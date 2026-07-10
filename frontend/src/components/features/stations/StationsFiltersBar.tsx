import { Filter, RotateCcw } from "lucide-react";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import {
  buildStationFiltersFromDraft,
  stationFiltersToDraft,
  type StationFiltersDraft,
} from "@/lib/stationFilters";
import type { StationFilters, StationStatus } from "@/types/api/stations";

const selectClass =
  "w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 shadow-sm outline-none transition-all duration-200 hover:border-slate-400 focus:border-brand focus:ring-2 focus:ring-blue-500/20";

const statuses: Array<{ value: "" | StationStatus; label: string }> = [
  { value: "", label: "All statuses" },
  { value: "active", label: "Active" },
  { value: "inactive", label: "Inactive" },
];

interface Props {
  filters: StationFilters;
  onApply: (filters: StationFilters) => void;
  onReset: () => void;
}

export function StationsFiltersBar({ filters, onApply, onReset }: Props) {
  const [draft, setDraft] = useState<StationFiltersDraft>(() => stationFiltersToDraft(filters));

  useEffect(() => {
    setDraft(stationFiltersToDraft(filters));
  }, [filters]);

  function updateDraft<K extends keyof StationFiltersDraft>(key: K, value: StationFiltersDraft[K]) {
    setDraft((current) => ({ ...current, [key]: value }));
  }

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onApply(
      buildStationFiltersFromDraft(draft, {
        page_size: filters.page_size,
        sort_by: filters.sort_by,
        sort_desc: filters.sort_desc,
      }),
    );
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="grid gap-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-soft md:grid-cols-2 xl:grid-cols-5"
    >
      <Input
        name="search"
        label="Search"
        value={draft.search}
        onChange={(event) => updateDraft("search", event.target.value)}
        placeholder="Station name, code, district"
      />
      <Input
        name="district"
        label="District"
        value={draft.district}
        onChange={(event) => updateDraft("district", event.target.value)}
      />
      <Input
        name="state"
        label="State"
        value={draft.state}
        onChange={(event) => updateDraft("state", event.target.value)}
      />
      <label className="block text-sm">
        <span className="mb-1.5 block font-medium text-slate-700">Status</span>
        <select
          name="status"
          value={draft.status}
          onChange={(event) => updateDraft("status", event.target.value)}
          className={selectClass}
        >
          {statuses.map((status) => (
            <option key={status.label} value={status.value}>
              {status.label}
            </option>
          ))}
        </select>
      </label>
      <Input
        name="station_type"
        label="Station Type"
        value={draft.station_type}
        onChange={(event) => updateDraft("station_type", event.target.value)}
      />
      <div className="flex items-end gap-2 xl:col-span-5">
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
