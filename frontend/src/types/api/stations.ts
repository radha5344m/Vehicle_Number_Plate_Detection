export type StationStatus = "active" | "inactive";

export interface StationItem {
  station_id: string;
  station_name: string;
  station_code: string;
  district: string;
  state: string;
  address: string;
  pincode: string;
  phone_number: string | null;
  email: string | null;
  station_type: string;
  status: StationStatus;
  created_at: string;
  updated_at: string;
}

export interface StationsPagination {
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
}

export interface StationsList {
  items: StationItem[];
  pagination: StationsPagination;
}

export interface StationFilters {
  search?: string;
  district?: string;
  state?: string;
  status?: StationStatus;
  station_type?: string;
  page?: number;
  page_size?: number;
  sort_by?: string;
  sort_desc?: boolean;
}

export interface CreateStationRequest {
  station_name: string;
  station_code: string;
  district: string;
  state: string;
  address: string;
  pincode: string;
  phone_number?: string;
  email?: string;
  station_type: string;
  status: StationStatus;
}

export interface UpdateStationRequest {
  station_name: string;
  district: string;
  state: string;
  address: string;
  pincode: string;
  phone_number?: string;
  email?: string;
  station_type: string;
  status: StationStatus;
}

export interface StationMutationResult {
  station: StationItem;
}

export interface ActionMessage {
  message: string;
}
