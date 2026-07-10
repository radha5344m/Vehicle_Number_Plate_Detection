import { deleteApiData, getApiData, patchApiData, postApiData, putApiData } from "@/services/api/httpClient";
import type {
  ActionMessage,
  CreateStationRequest,
  StationFilters,
  StationMutationResult,
  StationsList,
  StationStatus,
  UpdateStationRequest,
} from "@/types/api/stations";

function toQueryString(filters: StationFilters): string {
  const params = new URLSearchParams();
  if (filters.search) params.set("search", filters.search);
  if (filters.district) params.set("district", filters.district);
  if (filters.state) params.set("state", filters.state);
  if (filters.status) params.set("status", filters.status);
  if (filters.station_type) params.set("station_type", filters.station_type);
  if (filters.page) params.set("page", String(filters.page));
  if (filters.page_size) params.set("page_size", String(filters.page_size));
  if (filters.sort_by) params.set("sort_by", filters.sort_by);
  if (filters.sort_desc != null) params.set("sort_desc", String(filters.sort_desc));
  const query = params.toString();
  return query ? `?${query}` : "";
}

export const stationsService = {
  list(filters: StationFilters = {}): Promise<StationsList> {
    return getApiData<StationsList>(`/v1/stations${toQueryString(filters)}`);
  },

  create(body: CreateStationRequest): Promise<StationMutationResult> {
    return postApiData<StationMutationResult>("/v1/stations", body);
  },

  update(stationId: string, body: UpdateStationRequest): Promise<StationMutationResult> {
    return putApiData<StationMutationResult>(`/v1/stations/${stationId}`, body);
  },

  changeStatus(stationId: string, status: StationStatus): Promise<StationMutationResult> {
    return patchApiData<StationMutationResult>(`/v1/stations/${stationId}/status`, { status });
  },

  delete(stationId: string): Promise<ActionMessage> {
    return deleteApiData<ActionMessage>(`/v1/stations/${stationId}`);
  },
};
