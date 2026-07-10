import { describe, expect, it } from "vitest";

import {
  formatInr,
  formatVerificationStatus,
  resolveChallanSummary,
  resolveVehicleName,
} from "@/lib/fieldVerificationSummary";
import type { VehicleVerificationWorkflowResult } from "@/types/api/workflow";

function baseResult(
  overrides: Partial<VehicleVerificationWorkflowResult> = {},
): VehicleVerificationWorkflowResult {
  return {
    status: "completed",
    workflow_id: "wf-1",
    registration_number: "AP09AB1234",
    vision_confidence: 0.92,
    vehicle_information: {
      vehicle_id: "v-1",
      plate_number: "AP09AB1234",
      jurisdiction: "AP",
      make: "Toyota",
      model: "Innova Crysta",
      color: "White",
      year: 2020,
      vehicle_type: "car",
      registration_status: "active",
      registered_owner: "Ravi Kumar",
    },
    vision_attributes: {
      color: "White",
      vehicle_type: "car",
      brand: "Toyota",
      color_confidence: 0.9,
      vehicle_type_confidence: 0.88,
      brand_confidence: 0.91,
      model_version: "gemini",
    },
    vehicle_model: "Innova Crysta",
    vision_explanation: null,
    attribute_comparison: null,
    verification_result: { lookup_status: "found", message: "Vehicle found" },
    risk_score: 0.2,
    risk_level: "low",
    risk_explanation: null,
    recommendation: "Proceed with routine checks.",
    investigation_summary: null,
    scan_id: "scan-1",
    report_id: "report-1",
    report_download_url: "/v1/reports/report-1/download",
    failed_stage: null,
    failure_message: null,
    total_duration_ms: 1200,
    completed_at: "2026-07-09T00:00:00.000Z",
    ...overrides,
  };
}

describe("fieldVerificationSummary", () => {
  it("formats verification status labels", () => {
    expect(formatVerificationStatus("found")).toBe("Found");
    expect(formatVerificationStatus("not_found")).toBe("Not Found");
  });

  it("builds vehicle name from registry and vision data", () => {
    expect(resolveVehicleName(baseResult())).toBe("Toyota Innova Crysta");
  });

  it("defaults challan summary when lookup data is unavailable", () => {
    expect(resolveChallanSummary(baseResult())).toEqual({
      outstandingFineInr: 0,
      pendingChallansCount: 0,
      latestViolation: null,
      statusLabel: "No Pending Challans",
    });
  });

  it("uses outstanding fine fields when provided", () => {
    expect(
      resolveChallanSummary(
        baseResult({
          outstanding_fine_inr: 1500,
          pending_challans_count: 2,
          latest_violation: "SIGNAL_JUMP",
        }),
      ),
    ).toEqual({
      outstandingFineInr: 1500,
      pendingChallansCount: 2,
      latestViolation: "SIGNAL_JUMP",
      statusLabel: "2 Pending Challans",
    });
    expect(formatInr(1500)).toBe("₹1,500");
  });
});
