import { toDateInputValue } from "@/lib/userFilters";
import type {
  InvestigationReportsFilters,
  RiskLevel,
  VerificationStatus,
} from "@/types/api/investigationReports";

export const DEFAULT_INVESTIGATION_REPORTS_FILTERS: InvestigationReportsFilters = {
  page: 1,
  page_size: 20,
  sort_by: "scanned_at",
  sort_desc: true,
};

export interface InvestigationReportFiltersDraft {
  search: string;
  from: string;
  to: string;
  officer: string;
  police_station: string;
  district: string;
  owner_name: string;
  risk_level: string;
  vehicle_type: string;
  vehicle_brand: string;
  registration_number: string;
  investigation_status: string;
  verification_status: string;
  ai_confidence_min: string;
  ai_confidence_max: string;
}

export function investigationFiltersToDraft(
  filters: InvestigationReportsFilters,
): InvestigationReportFiltersDraft {
  return {
    search: filters.search ?? "",
    from: toDateInputValue(filters.from),
    to: toDateInputValue(filters.to),
    officer: filters.officer ?? "",
    police_station: filters.police_station ?? "",
    district: filters.district ?? "",
    owner_name: filters.owner_name ?? "",
    risk_level: filters.risk_level ?? "",
    vehicle_type: filters.vehicle_type ?? "",
    vehicle_brand: filters.vehicle_brand ?? "",
    registration_number: filters.registration_number ?? "",
    investigation_status: filters.investigation_status ?? "",
    verification_status: filters.verification_status ?? "",
    ai_confidence_min:
      filters.ai_confidence_min != null
        ? String(Math.round(filters.ai_confidence_min * 100))
        : "",
    ai_confidence_max:
      filters.ai_confidence_max != null
        ? String(Math.round(filters.ai_confidence_max * 100))
        : "",
  };
}

export function validateInvestigationDateRange(from: string, to: string): string | null {
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

export function buildInvestigationFiltersFromDraft(
  draft: InvestigationReportFiltersDraft,
  base: Pick<InvestigationReportsFilters, "page_size" | "sort_by" | "sort_desc">,
): InvestigationReportsFilters {
  const minConfidence = draft.ai_confidence_min.trim();
  const maxConfidence = draft.ai_confidence_max.trim();

  return {
    from: draft.from ? new Date(draft.from).toISOString() : undefined,
    to: draft.to ? new Date(`${draft.to}T23:59:59`).toISOString() : undefined,
    search: draft.search.trim() || undefined,
    officer: draft.officer.trim() || undefined,
    police_station: draft.police_station.trim() || undefined,
    district: draft.district.trim() || undefined,
    risk_level: (draft.risk_level || undefined) as RiskLevel | undefined,
    vehicle_type: draft.vehicle_type.trim() || undefined,
    vehicle_brand: draft.vehicle_brand.trim() || undefined,
    registration_number: draft.registration_number.trim() || undefined,
    owner_name: draft.owner_name.trim() || undefined,
    verification_status: (draft.verification_status || undefined) as VerificationStatus | undefined,
    investigation_status: (draft.investigation_status || undefined) as
      | "completed"
      | "pending"
      | undefined,
    ai_confidence_min: minConfidence ? Number(minConfidence) / 100 : undefined,
    ai_confidence_max: maxConfidence ? Number(maxConfidence) / 100 : undefined,
    page: 1,
    page_size: base.page_size ?? 20,
    sort_by: base.sort_by ?? "scanned_at",
    sort_desc: base.sort_desc ?? true,
  };
}
