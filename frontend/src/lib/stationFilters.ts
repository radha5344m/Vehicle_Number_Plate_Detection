import type { StationFilters, StationStatus } from "@/types/api/stations";

export const DEFAULT_STATION_FILTERS: StationFilters = {
  page: 1,
  page_size: 20,
  sort_by: "created_at",
  sort_desc: true,
};

export interface StationFiltersDraft {
  search: string;
  district: string;
  state: string;
  status: string;
  station_type: string;
}

export function stationFiltersToDraft(filters: StationFilters): StationFiltersDraft {
  return {
    search: filters.search ?? "",
    district: filters.district ?? "",
    state: filters.state ?? "",
    status: filters.status ?? "",
    station_type: filters.station_type ?? "",
  };
}

export function buildStationFiltersFromDraft(
  draft: StationFiltersDraft,
  base: Pick<StationFilters, "page_size" | "sort_by" | "sort_desc">,
): StationFilters {
  return {
    search: draft.search.trim() || undefined,
    district: draft.district.trim() || undefined,
    state: draft.state.trim() || undefined,
    status: (draft.status || undefined) as StationStatus | undefined,
    station_type: draft.station_type.trim() || undefined,
    page: 1,
    page_size: base.page_size ?? 20,
    sort_by: base.sort_by ?? "created_at",
    sort_desc: base.sort_desc ?? true,
  };
}
