import { Filter, RotateCcw } from "lucide-react";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import {
  buildInvestigationFiltersFromDraft,
  investigationFiltersToDraft,
  validateInvestigationDateRange,
  type InvestigationReportFiltersDraft,
} from "@/lib/investigationReportFilters";
import type {
  InvestigationReportsFilters,
  RiskLevel,
  VerificationStatus,
} from "@/types/api/investigationReports";

const riskLevels: Array<{ value: "" | RiskLevel; label: string }> = [
  { value: "", label: "All risk levels" },
  { value: "low", label: "Low" },
  { value: "medium", label: "Medium" },
  { value: "high", label: "High" },
  { value: "critical", label: "Critical" },
];

const verificationStatuses: Array<{ value: "" | VerificationStatus; label: string }> = [
  { value: "", label: "All verification statuses" },
  { value: "found", label: "Verified / Found" },
  { value: "not_found", label: "Not Found" },
  { value: "pending", label: "Pending" },
  { value: "unknown", label: "Unknown" },
];

const investigationStatuses = [
  { value: "", label: "All investigation statuses" },
  { value: "completed", label: "Completed" },
  { value: "pending", label: "Pending" },
] as const;

const selectClass =
  "w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 shadow-sm outline-none transition-all duration-200 hover:border-slate-400 focus:border-brand focus:ring-2 focus:ring-blue-500/20";

interface Props {
  filters: InvestigationReportsFilters;
  onApply: (filters: InvestigationReportsFilters) => void;
  onReset: () => void;
  submitLabel?: string;
}

export function OfficerReportsFiltersBar({
  filters,
  onApply,
  onReset,
  submitLabel = "Apply Filters",
}: Props) {
  const [draft, setDraft] = useState<InvestigationReportFiltersDraft>(() =>
    investigationFiltersToDraft(filters),
  );
  const [dateError, setDateError] = useState<string | null>(null);

  useEffect(() => {
    setDraft(investigationFiltersToDraft(filters));
    setDateError(null);
  }, [filters]);

  function updateDraft<K extends keyof InvestigationReportFiltersDraft>(
    key: K,
    value: InvestigationReportFiltersDraft[K],
  ) {
    setDraft((current) => ({ ...current, [key]: value }));
    if (key === "from" || key === "to") {
      setDateError(null);
    }
  }

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const rangeError = validateInvestigationDateRange(draft.from, draft.to);
    if (rangeError) {
      setDateError(rangeError);
      return;
    }
    setDateError(null);
    onApply(
      buildInvestigationFiltersFromDraft(draft, {
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
    <form
      onSubmit={handleSubmit}
      className="grid gap-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-soft md:grid-cols-2 xl:grid-cols-5"
    >
      <Input
        name="search"
        label="Global Search"
        value={draft.search}
        onChange={(event) => updateDraft("search", event.target.value)}
        placeholder="Reg no / owner / vehicle / ID"
      />
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
      <label className="block text-sm">
        <span className="mb-1.5 block font-medium text-slate-700">Risk Level</span>
        <select
          name="risk_level"
          value={draft.risk_level}
          onChange={(event) => updateDraft("risk_level", event.target.value)}
          className={selectClass}
        >
          {riskLevels.map((level) => (
            <option key={level.label} value={level.value}>
              {level.label}
            </option>
          ))}
        </select>
      </label>
      <Input
        name="vehicle_type"
        label="Vehicle Type"
        value={draft.vehicle_type}
        onChange={(event) => updateDraft("vehicle_type", event.target.value)}
      />
      <Input
        name="vehicle_brand"
        label="Vehicle Brand"
        value={draft.vehicle_brand}
        onChange={(event) => updateDraft("vehicle_brand", event.target.value)}
      />
      <Input
        name="registration_number"
        label="Registration Number"
        value={draft.registration_number}
        onChange={(event) => updateDraft("registration_number", event.target.value)}
        className="font-mono"
      />
      <Input
        name="owner_name"
        label="Owner Name"
        value={draft.owner_name}
        onChange={(event) => updateDraft("owner_name", event.target.value)}
      />
      <Input
        name="ai_confidence_min"
        label="AI Confidence Min (%)"
        type="number"
        min="0"
        max="100"
        value={draft.ai_confidence_min}
        onChange={(event) => updateDraft("ai_confidence_min", event.target.value)}
      />
      <Input
        name="ai_confidence_max"
        label="AI Confidence Max (%)"
        type="number"
        min="0"
        max="100"
        value={draft.ai_confidence_max}
        onChange={(event) => updateDraft("ai_confidence_max", event.target.value)}
      />
      <label className="block text-sm">
        <span className="mb-1.5 block font-medium text-slate-700">Investigation Status</span>
        <select
          name="investigation_status"
          value={draft.investigation_status}
          onChange={(event) => updateDraft("investigation_status", event.target.value)}
          className={selectClass}
        >
          {investigationStatuses.map((status) => (
            <option key={status.label} value={status.value}>
              {status.label}
            </option>
          ))}
        </select>
      </label>
      <label className="block text-sm">
        <span className="mb-1.5 block font-medium text-slate-700">Verification Status</span>
        <select
          name="verification_status"
          value={draft.verification_status}
          onChange={(event) => updateDraft("verification_status", event.target.value)}
          className={selectClass}
        >
          {verificationStatuses.map((status) => (
            <option key={status.label} value={status.value}>
              {status.label}
            </option>
          ))}
        </select>
      </label>
      {dateError && <p className="text-sm text-red-600 xl:col-span-5">{dateError}</p>}
      <div className="flex items-end gap-2 xl:col-span-2">
        <Button type="submit" icon={<Filter className="h-4 w-4" />}>
          {submitLabel}
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
