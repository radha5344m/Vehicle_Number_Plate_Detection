import { toDateInputValue } from "@/lib/userFilters";
import type { RiskLevel, ScanHistoryFilters } from "@/types/api/history";

export const DEFAULT_SCAN_HISTORY_FILTERS: ScanHistoryFilters = {};

export interface ScanHistoryFiltersDraft {
  plate: string;
  officer_id: string;
  risk_level: string;
  from: string;
  to: string;
}

export function scanHistoryFiltersToDraft(filters: ScanHistoryFilters): ScanHistoryFiltersDraft {
  return {
    plate: filters.plate ?? "",
    officer_id: filters.officer_id ?? "",
    risk_level: filters.risk_level ?? "",
    from: toDateInputValue(filters.from),
    to: toDateInputValue(filters.to),
  };
}

export function validateScanHistoryDateRange(from: string, to: string): string | null {
  if (!from || !to) return null;
  const fromDate = new Date(from);
  const toDate = new Date(`${to}T23:59:59`);
  if (Number.isNaN(fromDate.getTime()) || Number.isNaN(toDate.getTime())) {
    return "Enter valid date values.";
  }
  if (fromDate > toDate) {
    return "From Date must be on or before To Date.";
  }
  return null;
}

export function buildScanHistoryFiltersFromDraft(draft: ScanHistoryFiltersDraft): ScanHistoryFilters {
  return {
    plate: draft.plate.trim() || undefined,
    officer_id: draft.officer_id || undefined,
    risk_level: (draft.risk_level || undefined) as RiskLevel | undefined,
    from: draft.from ? new Date(draft.from).toISOString() : undefined,
    to: draft.to ? new Date(`${draft.to}T23:59:59`).toISOString() : undefined,
  };
}
