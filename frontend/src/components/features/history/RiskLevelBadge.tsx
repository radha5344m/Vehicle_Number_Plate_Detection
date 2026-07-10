import type { RiskLevel } from "@/types/api/history";

const RISK_STYLES: Record<RiskLevel, string> = {
  low: "border-green-200 bg-green-50 text-green-700",
  medium: "border-amber-200 bg-amber-50 text-amber-700",
  high: "border-orange-200 bg-orange-50 text-orange-700",
  critical: "border-red-200 bg-red-50 text-red-700",
};

interface RiskLevelBadgeProps {
  level: RiskLevel;
}

export function RiskLevelBadge({ level }: RiskLevelBadgeProps) {
  return (
    <span
      className={`inline-flex rounded-full border px-2.5 py-0.5 text-xs font-semibold capitalize ${RISK_STYLES[level]}`}
    >
      {level}
    </span>
  );
}
