import { Filter, RotateCcw } from "lucide-react";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import {
  buildScanHistoryFiltersFromDraft,
  scanHistoryFiltersToDraft,
  validateScanHistoryDateRange,
  type ScanHistoryFiltersDraft,
} from "@/lib/scanHistoryFilters";
import type { RiskLevel, ScanHistoryFilters } from "@/types/api/history";

const DEMO_OFFICERS = [
  { id: "", label: "All officers" },
  { id: "11111111-1111-1111-1111-111111111111", label: "Ravi Kumar" },
  { id: "33333333-3333-3333-3333-333333333333", label: "Sita Devi" },
] as const;

const RISK_LEVELS: Array<{ value: "" | RiskLevel; label: string }> = [
  { value: "", label: "All risk levels" },
  { value: "low", label: "Low" },
  { value: "medium", label: "Medium" },
  { value: "high", label: "High" },
  { value: "critical", label: "Critical" },
];

const selectClass =
  "w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 shadow-sm outline-none transition-all duration-200 hover:border-slate-400 focus:border-brand focus:ring-2 focus:ring-blue-500/20";

interface ScanHistoryFiltersBarProps {
  filters: ScanHistoryFilters;
  onApply: (filters: ScanHistoryFilters) => void;
  onReset: () => void;
}

export function ScanHistoryFiltersBar({ filters, onApply, onReset }: ScanHistoryFiltersBarProps) {
  const [draft, setDraft] = useState<ScanHistoryFiltersDraft>(() => scanHistoryFiltersToDraft(filters));
  const [dateError, setDateError] = useState<string | null>(null);

  useEffect(() => {
    setDraft(scanHistoryFiltersToDraft(filters));
    setDateError(null);
  }, [filters]);

  function updateDraft<K extends keyof ScanHistoryFiltersDraft>(
    key: K,
    value: ScanHistoryFiltersDraft[K],
  ) {
    setDraft((current) => ({ ...current, [key]: value }));
    if (key === "from" || key === "to") {
      setDateError(null);
    }
  }

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const rangeError = validateScanHistoryDateRange(draft.from, draft.to);
    if (rangeError) {
      setDateError(rangeError);
      return;
    }
    setDateError(null);
    onApply(buildScanHistoryFiltersFromDraft(draft));
  }

  function handleReset() {
    setDateError(null);
    onReset();
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="grid gap-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-soft md:grid-cols-2 lg:grid-cols-3"
    >
      <Input
        name="plate"
        label="Vehicle Number"
        value={draft.plate}
        onChange={(event) => updateDraft("plate", event.target.value)}
        placeholder="e.g. AP09AB1234"
        className="font-mono"
      />

      <label className="block text-sm">
        <span className="mb-1.5 block font-medium text-slate-700">Officer</span>
        <select
          name="officer_id"
          value={draft.officer_id}
          onChange={(event) => updateDraft("officer_id", event.target.value)}
          className={selectClass}
        >
          {DEMO_OFFICERS.map((officer) => (
            <option key={officer.id || "all"} value={officer.id}>
              {officer.label}
            </option>
          ))}
        </select>
      </label>

      <label className="block text-sm">
        <span className="mb-1.5 block font-medium text-slate-700">Risk Level</span>
        <select
          name="risk_level"
          value={draft.risk_level}
          onChange={(event) => updateDraft("risk_level", event.target.value)}
          className={selectClass}
        >
          {RISK_LEVELS.map((level) => (
            <option key={level.value || "all"} value={level.value}>
              {level.label}
            </option>
          ))}
        </select>
      </label>

      <Input
        type="date"
        name="from"
        label="From Date"
        value={draft.from}
        onChange={(event) => updateDraft("from", event.target.value)}
      />
      <Input
        type="date"
        name="to"
        label="To Date"
        value={draft.to}
        onChange={(event) => updateDraft("to", event.target.value)}
      />

      {dateError && <p className="text-sm text-red-600 lg:col-span-3">{dateError}</p>}

      <div className="flex items-end gap-2 lg:col-span-3">
        <Button type="submit" icon={<Filter className="h-4 w-4" />} className="w-full md:w-auto">
          Apply Filters
        </Button>
        <Button
          type="button"
          variant="secondary"
          icon={<RotateCcw className="h-4 w-4" />}
          onClick={handleReset}
        >
          Reset Filters
        </Button>
      </div>
    </form>
  );
}
