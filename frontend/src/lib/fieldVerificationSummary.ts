import type { VehicleVerificationWorkflowResult } from "@/types/api/workflow";

export interface ChallanSummary {
  outstandingFineInr: number;
  pendingChallansCount: number;
  latestViolation: string | null;
  statusLabel: string;
}

function orDash(value: string | null | undefined): string {
  const text = value?.trim();
  return text ? text : "—";
}

export function formatVerificationStatus(lookupStatus: string | null | undefined): string {
  if (lookupStatus === "found") return "Found";
  if (lookupStatus === "not_found") return "Not Found";
  if (!lookupStatus) return "—";
  return lookupStatus.replaceAll("_", " ").replace(/\b\w/g, (char) => char.toUpperCase());
}

export function formatRiskScore(score: number | null | undefined): string {
  if (score == null) return "—";
  return String(Math.round(score * 100));
}

export function formatConfidencePercent(value: number | null | undefined): string {
  if (value == null) return "—";
  return `${(value * 100).toFixed(0)}%`;
}

export function formatInr(amount: number): string {
  return `₹${amount.toLocaleString("en-IN")}`;
}

/** Vision-only registration number from workflow / Gemini output. */
export function resolveVisionRegistrationNumber(
  result: VehicleVerificationWorkflowResult,
): string {
  return orDash(result.registration_number);
}

/** Vision-only brand from Gemini attributes. */
export function resolveVisionBrand(result: VehicleVerificationWorkflowResult): string {
  return orDash(result.vision_attributes?.brand);
}

/** Vision-only model from Gemini output. */
export function resolveVisionModel(result: VehicleVerificationWorkflowResult): string {
  return orDash(result.vehicle_model);
}

/** Vision-only color from Gemini attributes. */
export function resolveVisionColor(result: VehicleVerificationWorkflowResult): string {
  return orDash(result.vision_attributes?.color);
}

/** Vision-only vehicle type from Gemini attributes. */
export function resolveVisionVehicleType(result: VehicleVerificationWorkflowResult): string {
  return orDash(result.vision_attributes?.vehicle_type);
}

export function resolveVisionVehicleName(result: VehicleVerificationWorkflowResult): string {
  const brand = result.vision_attributes?.brand?.trim() || "";
  const model = result.vehicle_model?.trim() || "";
  const combined = [brand, model].filter(Boolean).join(" ").trim();
  if (combined) return combined;
  return orDash(result.vision_attributes?.vehicle_type);
}

/** Registry-only make from database record. */
export function resolveRegistryMake(result: VehicleVerificationWorkflowResult): string {
  return orDash(result.vehicle_information?.make);
}

/** Registry-only model from database record. */
export function resolveRegistryModel(result: VehicleVerificationWorkflowResult): string {
  return orDash(result.vehicle_information?.model);
}

/** Registry-only color from database record. */
export function resolveRegistryColor(result: VehicleVerificationWorkflowResult): string {
  return orDash(result.vehicle_information?.color);
}

/** Registry-only vehicle type from database record. */
export function resolveRegistryVehicleType(result: VehicleVerificationWorkflowResult): string {
  return orDash(result.vehicle_information?.vehicle_type);
}

export function resolveRegistryVehicleName(result: VehicleVerificationWorkflowResult): string {
  const vehicle = result.vehicle_information;
  const make = vehicle?.make?.trim() || "";
  const model = vehicle?.model?.trim() || "";
  const combined = [make, model].filter(Boolean).join(" ").trim();
  if (combined) return combined;
  return orDash(vehicle?.vehicle_type);
}

export function resolveOwnerName(result: VehicleVerificationWorkflowResult): string {
  return orDash(result.vehicle_information?.registered_owner);
}

export function resolveChallanSummary(result: VehicleVerificationWorkflowResult): ChallanSummary {
  const vehicle = result.vehicle_information;
  const pendingChallansCount =
    result.pending_challans_count ?? vehicle?.pending_challans_count ?? 0;
  const outstandingFineInr =
    result.outstanding_fine_inr ?? vehicle?.outstanding_fine_inr ?? 0;
  const latestViolation = result.latest_violation ?? null;

  return {
    outstandingFineInr,
    pendingChallansCount,
    latestViolation,
    statusLabel:
      pendingChallansCount > 0
        ? `${pendingChallansCount} Pending Challan${pendingChallansCount === 1 ? "" : "s"}`
        : "No Pending Challans",
  };
}

export function formatViolationLabel(code: string): string {
  return code.replaceAll("_", " ").replace(/\b\w/g, (char) => char.toUpperCase());
}
