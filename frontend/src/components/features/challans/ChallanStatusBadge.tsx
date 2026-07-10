import { Badge } from "@/components/ui/Badge";
import type { ChallanPaymentStatus } from "@/types/api/challans";

const STATUS_LABELS: Record<ChallanPaymentStatus, string> = {
  pending: "Pending",
  paid: "Paid",
  cancelled: "Cancelled",
  waived: "Waived",
};

const STATUS_VARIANTS: Record<ChallanPaymentStatus, "warning" | "success" | "danger" | "default"> = {
  pending: "warning",
  paid: "success",
  cancelled: "danger",
  waived: "default",
};

export function ChallanStatusBadge({ status }: { status: ChallanPaymentStatus | string }) {
  const normalized = status.toLowerCase() as ChallanPaymentStatus;
  const label = STATUS_LABELS[normalized] ?? status;
  const variant = STATUS_VARIANTS[normalized] ?? "default";
  return <Badge variant={variant}>{label}</Badge>;
}

export function formatChallanInr(amount: number): string {
  return `₹${amount.toLocaleString("en-IN")}`;
}

export function formatViolationLabel(code: string): string {
  return code.replaceAll("_", " ").replace(/\b\w/g, (char) => char.toUpperCase());
}
