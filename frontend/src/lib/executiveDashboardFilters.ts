import { toDateInputValue } from "@/lib/userFilters";
import type { ExecutiveDashboardFilters } from "@/types/api/executiveDashboard";

export const DEFAULT_EXECUTIVE_DASHBOARD_FILTERS: ExecutiveDashboardFilters = {};

export interface ExecutiveDashboardFiltersDraft {
  from: string;
  to: string;
  district: string;
  station: string;
  officer: string;
  vehicle_type: string;
  risk_level: string;
  brand: string;
}

export function executiveDashboardFiltersToDraft(
  filters: ExecutiveDashboardFilters,
): ExecutiveDashboardFiltersDraft {
  return {
    from: toDateInputValue(filters.from),
    to: toDateInputValue(filters.to),
    district: filters.district ?? "",
    station: filters.station ?? "",
    officer: filters.officer ?? "",
    vehicle_type: filters.vehicle_type ?? "",
    risk_level: filters.risk_level ?? "",
    brand: filters.brand ?? "",
  };
}

export function validateExecutiveDashboardDateRange(from: string, to: string): string | null {
  if (!from || !to) return null;
  const fromDate = new Date(from);
  const toDate = new Date(`${to}T23:59:59`);
  if (Number.isNaN(fromDate.getTime()) || Number.isNaN(toDate.getTime())) {
    return "Enter valid date values.";
  }
  if (fromDate > toDate) {
    return "From must be on or before To.";
  }
  return null;
}

export function buildExecutiveDashboardFiltersFromDraft(
  draft: ExecutiveDashboardFiltersDraft,
): ExecutiveDashboardFilters {
  return {
    from: draft.from ? new Date(draft.from).toISOString() : undefined,
    to: draft.to ? new Date(`${draft.to}T23:59:59`).toISOString() : undefined,
    district: draft.district.trim() || undefined,
    station: draft.station.trim() || undefined,
    officer: draft.officer.trim() || undefined,
    vehicle_type: draft.vehicle_type.trim() || undefined,
    risk_level: draft.risk_level || undefined,
    brand: draft.brand.trim() || undefined,
  };
}
