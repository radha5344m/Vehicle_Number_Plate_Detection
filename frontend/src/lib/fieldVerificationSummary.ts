import type { VehicleVerificationWorkflowResult } from "@/types/api/workflow";

export interface ChallanSummary {
  outstandingFineInr: number;
  pendingChallansCount: number;
  latestViolation: string | null;
  statusLabel: string;
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

export function resolveVehicleName(result: VehicleVerificationWorkflowResult): string {
  const vehicle = result.vehicle_information;
  const vision = result.vision_attributes;
  const make = vehicle?.make?.trim() || vision?.brand?.trim() || "";
  const model = vehicle?.model?.trim() || result.vehicle_model?.trim() || "";
  const combined = [make, model].filter(Boolean).join(" ").trim();
  if (combined) return combined;
  return vehicle?.vehicle_type?.trim() || vision?.vehicle_type?.trim() || "—";
}

export function resolveBrand(result: VehicleVerificationWorkflowResult): string {
  return (
    result.vision_attributes?.brand?.trim() ||
    result.vehicle_information?.make?.trim() ||
    "—"
  );
}

export function resolveModel(result: VehicleVerificationWorkflowResult): string {
  return result.vehicle_model?.trim() || result.vehicle_information?.model?.trim() || "—";
}

export function resolveColor(result: VehicleVerificationWorkflowResult): string {
  return (
    result.vision_attributes?.color?.trim() ||
    result.vehicle_information?.color?.trim() ||
    "—"
  );
}

export function resolveVehicleType(result: VehicleVerificationWorkflowResult): string {
  return (
    result.vision_attributes?.vehicle_type?.trim() ||
    result.vehicle_information?.vehicle_type?.trim() ||
    "—"
  );
}

export function resolveOwnerName(result: VehicleVerificationWorkflowResult): string {
  return result.vehicle_information?.registered_owner?.trim() || "—";
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
