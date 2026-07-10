import { toDateInputValue } from "@/lib/userFilters";

export interface DateRangeDraft {
  from: string;
  to: string;
}

export const EMPTY_DATE_RANGE_DRAFT: DateRangeDraft = { from: "", to: "" };

export function dateRangeToDraft(filters: { from?: string; to?: string }): DateRangeDraft {
  return {
    from: toDateInputValue(filters.from),
    to: toDateInputValue(filters.to),
  };
}

export function validateDateRangeDraft(from: string, to: string): string | null {
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

export function buildDateRangeFilters(draft: DateRangeDraft): { from?: string; to?: string } {
  return {
    from: draft.from ? new Date(draft.from).toISOString() : undefined,
    to: draft.to ? new Date(`${draft.to}T23:59:59`).toISOString() : undefined,
  };
}
