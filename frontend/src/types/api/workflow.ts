export interface WorkflowStep {
  stage: string;
  status: string;
  message: string;
  duration_ms?: number | null;
}

export interface VerificationResult {
  lookup_status: string;
  message: string;
}

export interface VehicleRecord {
  vehicle_id: string;
  plate_number: string;
  jurisdiction: string;
  make: string | null;
  model: string | null;
  color: string | null;
  year: number | null;
  vehicle_type: string;
  registration_status: string;
  registered_owner: string | null;
  outstanding_fine_inr?: number | null;
  pending_challans_count?: number | null;
}

export interface VisionAttributes {
  color: string;
  vehicle_type: string;
  brand: string | null;
  color_confidence: number;
  vehicle_type_confidence: number;
  brand_confidence: number | null;
  model_version: string;
}

export interface AttributeComparisonItem {
  attribute: string;
  observed: string;
  registered: string | null;
  matches: boolean | null;
  confidence: number | null;
}

export interface AttributeComparison {
  items: AttributeComparisonItem[];
  overall_match: boolean | null;
}

export interface RiskSignal {
  name: string;
  weight: number;
  detail: string;
}

export interface VehicleVerificationWorkflowResult {
  status: string;
  workflow_id: string;
  steps?: WorkflowStep[];
  registration_number: string | null;
  vision_confidence: number | null;
  vehicle_information: VehicleRecord | null;
  vision_attributes: VisionAttributes | null;
  vehicle_model: string | null;
  vision_explanation: string | null;
  attribute_comparison: AttributeComparison | null;
  verification_result: VerificationResult | null;
  risk_score: number | null;
  risk_level: string | null;
  risk_explanation: string | null;
  recommendation: string | null;
  investigation_summary: string | null;
  risk_signals?: RiskSignal[];
  scan_id: string | null;
  report_id: string | null;
  report_download_url: string | null;
  failed_stage: string | null;
  failure_message: string | null;
  total_duration_ms: number | null;
  completed_at: string;
  outstanding_fine_inr?: number | null;
  pending_challans_count?: number | null;
  latest_violation?: string | null;
}

export const WORKFLOW_STAGE_LABELS: Record<string, string> = {
  upload: "Image Upload",
  vision_analysis: "Vision AI Analysis",
  registry_verification: "Vehicle Registry Verification",
  risk_assessment: "Risk Assessment",
  save_investigation: "Save Investigation",
  report_generation: "Report Generation",
};
