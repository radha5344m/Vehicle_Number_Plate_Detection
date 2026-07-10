import type { UserFilters } from "@/types/api/users";

export interface UserFiltersDraft {
  search: string;
  role: string;
  station: string;
  status: string;
  created_from: string;
  created_to: string;
}

export function toDateInputValue(iso: string | undefined): string {
  if (!iso) return "";
  const parsed = new Date(iso);
  if (Number.isNaN(parsed.getTime())) return "";
  return parsed.toISOString().slice(0, 10);
}

export function filtersToDraft(filters: UserFilters): UserFiltersDraft {
  return {
    search: filters.search ?? "",
    role: filters.role ?? "",
    station: filters.station ?? "",
    status: filters.status ?? "",
    created_from: toDateInputValue(filters.created_from),
    created_to: toDateInputValue(filters.created_to),
  };
}

export function validateDateRange(createdFrom: string, createdTo: string): string | null {
  if (!createdFrom || !createdTo) return null;
  const from = new Date(createdFrom);
  const to = new Date(`${createdTo}T23:59:59`);
  if (Number.isNaN(from.getTime()) || Number.isNaN(to.getTime())) {
    return "Enter valid created-date values.";
  }
  if (from > to) {
    return "Created From must be on or before Created To.";
  }
  return null;
}

export function buildUserFiltersFromDraft(
  draft: UserFiltersDraft,
  base: Pick<UserFilters, "page_size" | "sort_by" | "sort_desc">,
): UserFilters {
  return sanitizeUserFilters({
    search: draft.search.trim() || undefined,
    role: (draft.role || undefined) as UserFilters["role"],
    station: draft.station.trim() || undefined,
    status: (draft.status || undefined) as UserFilters["status"],
    created_from: draft.created_from ? new Date(draft.created_from).toISOString() : undefined,
    created_to: draft.created_to ? new Date(`${draft.created_to}T23:59:59`).toISOString() : undefined,
    page: 1,
    page_size: base.page_size ?? 20,
    sort_by: base.sort_by ?? "created_at",
    sort_desc: base.sort_desc ?? true,
  });
}

export function sanitizeUserFilters(filters: UserFilters): UserFilters {
  const page = Math.max(1, filters.page ?? 1);
  const page_size = Math.min(100, Math.max(1, filters.page_size ?? 20));

  let created_from = filters.created_from;
  let created_to = filters.created_to;

  if (created_from && Number.isNaN(new Date(created_from).getTime())) {
    created_from = undefined;
  }
  if (created_to && Number.isNaN(new Date(created_to).getTime())) {
    created_to = undefined;
  }
  if (created_from && created_to && new Date(created_from) > new Date(created_to)) {
    created_from = undefined;
    created_to = undefined;
  }

  return {
    ...filters,
    page,
    page_size,
    created_from,
    created_to,
  };
}

export function getUserFiltersValidationError(filters: UserFilters): string | null {
  const sanitized = sanitizeUserFilters(filters);

  if ((filters.page ?? 1) < 1) {
    return "Page number must be at least 1.";
  }
  if ((filters.page_size ?? 20) < 1 || (filters.page_size ?? 20) > 100) {
    return "Page size must be between 1 and 100.";
  }
  if (filters.created_from && Number.isNaN(new Date(filters.created_from).getTime())) {
    return "Created From date is invalid. Reset filters and try again.";
  }
  if (filters.created_to && Number.isNaN(new Date(filters.created_to).getTime())) {
    return "Created To date is invalid. Reset filters and try again.";
  }
  if (
    sanitized.created_from !== filters.created_from
    || sanitized.created_to !== filters.created_to
  ) {
    return "Created From must be on or before Created To. Reset filters or adjust the date range.";
  }
  return null;
}
