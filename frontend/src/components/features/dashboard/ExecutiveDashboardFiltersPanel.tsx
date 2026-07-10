import { Download, Printer, RefreshCw, RotateCcw } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import {
  buildExecutiveDashboardFiltersFromDraft,
  executiveDashboardFiltersToDraft,
  validateExecutiveDashboardDateRange,
  type ExecutiveDashboardFiltersDraft,
} from "@/lib/executiveDashboardFilters";
import type { ExecutiveDashboardFilters } from "@/types/api/executiveDashboard";

const inputClass = "mt-1 w-full rounded-lg border border-slate-200 px-3 py-2";

interface Props {
  filters: ExecutiveDashboardFilters;
  onApplyFilters: (filters: ExecutiveDashboardFilters) => void;
  onResetFilters: () => void;
  onRefresh: () => void;
  onExport: (format: "pdf" | "csv" | "excel") => Promise<void>;
}

export function ExecutiveDashboardFiltersPanel({
  filters,
  onApplyFilters,
  onResetFilters,
  onRefresh,
  onExport,
}: Props) {
  const riskOptions = useMemo(() => ["", "low", "medium", "high", "critical"], []);
  const [draft, setDraft] = useState<ExecutiveDashboardFiltersDraft>(() =>
    executiveDashboardFiltersToDraft(filters),
  );
  const [dateError, setDateError] = useState<string | null>(null);

  useEffect(() => {
    setDraft(executiveDashboardFiltersToDraft(filters));
    setDateError(null);
  }, [filters]);

  function updateDraft<K extends keyof ExecutiveDashboardFiltersDraft>(
    key: K,
    value: ExecutiveDashboardFiltersDraft[K],
  ) {
    setDraft((current) => ({ ...current, [key]: value }));
    if (key === "from" || key === "to") {
      setDateError(null);
    }
  }

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const rangeError = validateExecutiveDashboardDateRange(draft.from, draft.to);
    if (rangeError) {
      setDateError(rangeError);
      return;
    }
    setDateError(null);
    onApplyFilters(buildExecutiveDashboardFiltersFromDraft(draft));
  }

  function handleReset() {
    setDateError(null);
    onResetFilters();
  }

  return (
    <Card title="Executive Filters">
      <form className="grid gap-4 md:grid-cols-2 xl:grid-cols-4" onSubmit={handleSubmit}>
        <label className="text-sm text-slate-600">
          From
          <input
            name="from"
            type="date"
            value={draft.from}
            onChange={(event) => updateDraft("from", event.target.value)}
            className={inputClass}
          />
        </label>
        <label className="text-sm text-slate-600">
          To
          <input
            name="to"
            type="date"
            value={draft.to}
            onChange={(event) => updateDraft("to", event.target.value)}
            className={inputClass}
          />
        </label>
        <label className="text-sm text-slate-600">
          District
          <input
            name="district"
            value={draft.district}
            onChange={(event) => updateDraft("district", event.target.value)}
            className={inputClass}
          />
        </label>
        <label className="text-sm text-slate-600">
          Station
          <input
            name="station"
            value={draft.station}
            onChange={(event) => updateDraft("station", event.target.value)}
            className={inputClass}
          />
        </label>
        <label className="text-sm text-slate-600">
          Officer
          <input
            name="officer"
            value={draft.officer}
            onChange={(event) => updateDraft("officer", event.target.value)}
            className={inputClass}
          />
        </label>
        <label className="text-sm text-slate-600">
          Vehicle Type
          <input
            name="vehicle_type"
            value={draft.vehicle_type}
            onChange={(event) => updateDraft("vehicle_type", event.target.value)}
            className={inputClass}
          />
        </label>
        <label className="text-sm text-slate-600">
          Risk Level
          <select
            name="risk_level"
            value={draft.risk_level}
            onChange={(event) => updateDraft("risk_level", event.target.value)}
            className={inputClass}
          >
            {riskOptions.map((option) => (
              <option key={option || "all"} value={option}>
                {option ? option.toUpperCase() : "All"}
              </option>
            ))}
          </select>
        </label>
        <label className="text-sm text-slate-600">
          Brand
          <input
            name="brand"
            value={draft.brand}
            onChange={(event) => updateDraft("brand", event.target.value)}
            className={inputClass}
          />
        </label>
        {dateError && <p className="text-sm text-red-600 xl:col-span-4">{dateError}</p>}
        <div className="flex flex-wrap items-end gap-3 xl:col-span-4">
          <Button type="submit">Apply Filters</Button>
          <Button type="button" variant="secondary" icon={<RotateCcw className="h-4 w-4" />} onClick={handleReset}>
            Reset Filters
          </Button>
          <Button type="button" variant="secondary" onClick={onRefresh}>
            <RefreshCw className="h-4 w-4" />
            Refresh
          </Button>
          <Button type="button" variant="secondary" onClick={() => void onExport("pdf")}>
            <Download className="h-4 w-4" />
            Export PDF
          </Button>
          <Button type="button" variant="secondary" onClick={() => void onExport("excel")}>
            <Download className="h-4 w-4" />
            Export Excel
          </Button>
          <Button type="button" variant="secondary" onClick={() => void onExport("csv")}>
            <Download className="h-4 w-4" />
            Export CSV
          </Button>
          <Button type="button" variant="secondary" onClick={() => window.print()}>
            <Printer className="h-4 w-4" />
            Print
          </Button>
        </div>
      </form>
    </Card>
  );
}
