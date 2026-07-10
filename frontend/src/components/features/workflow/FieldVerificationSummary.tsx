import { Download, FileSearch, FileWarning, Plus } from "lucide-react";
import { useNavigate } from "react-router-dom";

import { RiskLevelBadge } from "@/components/features/history/RiskLevelBadge";
import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import {
  formatConfidencePercent,
  formatInr,
  formatRiskScore,
  formatVerificationStatus,
  formatViolationLabel,
  resolveBrand,
  resolveChallanSummary,
  resolveColor,
  resolveModel,
  resolveOwnerName,
  resolveVehicleName,
  resolveVehicleType,
} from "@/lib/fieldVerificationSummary";
import { PATHS } from "@/routes/paths";
import type { RiskLevel } from "@/types/api/history";
import { WORKFLOW_STAGE_LABELS, type VehicleVerificationWorkflowResult } from "@/types/api/workflow";

interface FieldVerificationSummaryProps {
  result: VehicleVerificationWorkflowResult;
  onViewDetailed: () => void;
  onDownloadPdf: () => void;
}

function SummaryRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-start justify-between gap-4 border-b border-slate-100 py-3 last:border-b-0">
      <dt className="text-sm text-slate-500">{label}</dt>
      <dd className="max-w-[60%] text-right text-sm font-semibold text-slate-900">{value}</dd>
    </div>
  );
}

function formatWorkflowFailureMessage(message: string | null | undefined): string | null {
  if (!message) return null;
  const lowered = message.toLowerCase();
  if (
    lowered.includes("temporarily unavailable") ||
    lowered.includes("high demand")
  ) {
    return "Vision AI service is temporarily unavailable due to high demand. Please try again in a few moments.";
  }
  if (
    lowered.includes("quota") ||
    lowered.includes("resource_exhausted") ||
    (message.includes("429") && lowered.includes("quota"))
  ) {
    return "Vision AI quota exceeded. Retry after checking provider usage.";
  }
  if (lowered.includes("api_key") && (lowered.includes("not set") || lowered.includes("invalid"))) {
    return "Vision AI is not configured on the server.";
  }
  return message;
}

export function FieldVerificationSummary({
  result,
  onViewDetailed,
  onDownloadPdf,
}: FieldVerificationSummaryProps) {
  const navigate = useNavigate();
  const completed = result.status === "completed";
  const registrationNumber = result.registration_number ?? "—";
  const verificationStatus = formatVerificationStatus(result.verification_result?.lookup_status);
  const challan = resolveChallanSummary(result);
  const failureMessage = formatWorkflowFailureMessage(result.failure_message);

  return (
    <div className="animate-slide-up space-y-5">
      <Alert
        variant={completed ? "success" : "warning"}
        title={completed ? "Verification Complete" : "Verification Incomplete"}
      >
        {result.failed_stage ? (
          <p className="text-sm">
            Failed at {WORKFLOW_STAGE_LABELS[result.failed_stage] ?? result.failed_stage}
            {failureMessage ? `: ${failureMessage}` : ""}
          </p>
        ) : (
          <p className="text-sm">
            Field summary for <span className="font-mono font-semibold">{registrationNumber}</span>
          </p>
        )}
      </Alert>

      <Card
        title="Field Verification Summary"
        description="Quick reference for patrol and checkpoint use"
        icon={<FileSearch className="h-4 w-4" />}
        accent
      >
        <dl>
          <SummaryRow label="Registration Number" value={registrationNumber} />
          <SummaryRow label="Verification Status" value={verificationStatus} />
          <SummaryRow label="Owner Name" value={resolveOwnerName(result)} />
          <SummaryRow label="Vehicle Name" value={resolveVehicleName(result)} />
          <SummaryRow label="Brand" value={resolveBrand(result)} />
          <SummaryRow label="Model" value={resolveModel(result)} />
          <SummaryRow label="Color" value={resolveColor(result)} />
          <SummaryRow label="Vehicle Type" value={resolveVehicleType(result)} />
          <SummaryRow
            label="Risk Level"
            value={(result.risk_level ?? "—").replaceAll("_", " ").toUpperCase()}
          />
          <SummaryRow
            label="Risk Score"
            value={result.risk_score != null ? `${formatRiskScore(result.risk_score)}/100` : "—"}
          />
          <SummaryRow
            label="Vision AI Confidence"
            value={formatConfidencePercent(result.vision_confidence)}
          />
          <SummaryRow label="Outstanding Fine" value={formatInr(challan.outstandingFineInr)} />
          <SummaryRow label="Pending Challans" value={String(challan.pendingChallansCount)} />
          <SummaryRow
            label="Latest Violation"
            value={challan.latestViolation ? formatViolationLabel(challan.latestViolation) : "—"}
          />
          <SummaryRow label="Status" value={challan.statusLabel} />
          <SummaryRow label="Recommended Action" value={result.recommendation?.trim() || "—"} />
        </dl>

        {result.risk_level ? (
          <div className="mt-4 flex justify-end">
            <RiskLevelBadge level={result.risk_level as RiskLevel} />
          </div>
        ) : null}
      </Card>

      <div className="flex flex-col gap-3 sm:flex-row sm:flex-wrap">
        <Button className="w-full sm:w-auto" icon={<FileSearch className="h-4 w-4" />} onClick={onViewDetailed}>
          View Detailed Investigation
        </Button>
        {result.registration_number ? (
          <>
            <Button
              className="w-full sm:w-auto"
              variant="secondary"
              icon={<FileWarning className="h-4 w-4" />}
              onClick={() =>
                navigate(
                  `${PATHS.ECHALLANS}?tab=history&registration=${encodeURIComponent(result.registration_number!)}`,
                )
              }
            >
              View Challans
            </Button>
            <Button
              className="w-full sm:w-auto"
              variant="secondary"
              icon={<Plus className="h-4 w-4" />}
              onClick={() =>
                navigate(
                  `${PATHS.ECHALLANS}?tab=issue&registration=${encodeURIComponent(result.registration_number!)}`,
                )
              }
            >
              Issue New Challan
            </Button>
          </>
        ) : null}
        {result.report_download_url ? (
          <Button
            className="w-full sm:w-auto"
            variant="secondary"
            icon={<Download className="h-4 w-4" />}
            onClick={onDownloadPdf}
          >
            Download PDF
          </Button>
        ) : null}
      </div>
    </div>
  );
}
