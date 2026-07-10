export type ChallanPaymentStatus = "pending" | "paid" | "cancelled" | "waived";

export interface ViolationMaster {
  violation_code: string;
  violation_name: string;
  default_fine_amount: number;
  amount_editable: boolean;
}

export interface ChallanItem {
  id: string;
  challan_number: string;
  registration_number: string;
  owner_name: string | null;
  violation_type: string;
  violation_description: string | null;
  fine_amount: number;
  payment_status: ChallanPaymentStatus;
  officer_id: string;
  officer_name: string;
  station_id: string;
  station_name: string;
  issued_at: string;
}

export interface ChallanDetail extends ChallanItem {
  investigation_id: string | null;
  vehicle_id: string | null;
  remarks: string | null;
  location_label: string | null;
  gps_coordinates: string | null;
  evidence_image_path: string | null;
  paid_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface ChallanPagination {
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
}

export interface ChallansListData {
  items: ChallanItem[];
  pagination: ChallanPagination;
}

export interface ChallanMutationData {
  challan: ChallanDetail;
  pdf_download_url?: string | null;
}

export interface ChallanSummary {
  outstanding_fine_inr: number;
  pending_challans_count: number;
  latest_violation: string | null;
}

export interface VehicleChallanSearchData {
  registration_number: string;
  vehicle_found: boolean;
  owner_name: string | null;
  vehicle_name: string | null;
  brand: string | null;
  model: string | null;
  color: string | null;
  vehicle_type: string | null;
  rc_status: string | null;
  insurance_status: string;
  pollution_status: string;
  risk_level: string | null;
  outstanding_fine_inr: number;
  pending_challans_count: number;
  previous_violations: string[];
  existing_challans: ChallanItem[];
  challan_summary: ChallanSummary;
}

export interface DistributionItem {
  label: string;
  value: number;
}

export interface MonthlyFineCollection {
  month: string;
  collected_fine_inr: number;
  issued_count: number;
}

export interface ChallanAnalyticsData {
  total_challans: number;
  todays_challans: number;
  pending_challans: number;
  paid_challans: number;
  collected_fine_inr: number;
  outstanding_fine_inr: number;
  most_common_violation: string | null;
  top_issuing_officer: string | null;
  top_station: string | null;
  violation_distribution: DistributionItem[];
  monthly_fine_collection: MonthlyFineCollection[];
}

export interface ChallansFilters {
  search?: string;
  registration_number?: string;
  challan_number?: string;
  owner_name?: string;
  officer_id?: string;
  station_id?: string;
  violation_type?: string;
  payment_status?: ChallanPaymentStatus;
  pending_only?: boolean;
  issued_from?: string;
  issued_to?: string;
  page?: number;
  page_size?: number;
}

export interface CreateChallanPayload {
  registration_number: string;
  owner_name?: string | null;
  vehicle_id?: string | null;
  investigation_id?: string | null;
  violation_type: string;
  violation_description?: string | null;
  fine_amount: number;
  remarks?: string | null;
  location_label?: string | null;
  gps_coordinates?: string | null;
}
