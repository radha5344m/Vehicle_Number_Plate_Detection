export type RiskLevel = "low" | "medium" | "high" | "critical";

export interface VehicleDetailsInput {
  plate_number?: string;
  make?: string;
  model?: string;
  color?: string;
  vehicle_type?: string;
  registration_status?: string;
  registered_owner?: string;
}

export interface GenerateInvestigationReportInput {
  detected_plate: string;
  ocr_registration_number: string;
  ocr_detected_text: string;
  ocr_confidence: number;
  risk_score: number;
  risk_level: RiskLevel;
  recommendation: string;
  title?: string;
  vehicle_details?: VehicleDetailsInput;
}

export interface InvestigationReportResult {
  report_id: string;
  title: string;
  file_size_bytes: number;
  checksum_sha256: string;
  generated_at: string;
  download_url: string;
}
