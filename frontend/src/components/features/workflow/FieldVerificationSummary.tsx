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
  resolveChallanSummary,
  resolveOwnerName,
  resolveRegistryColor,
  resolveRegistryMake,
  resolveRegistryModel,
  resolveRegistryVehicleType,
  resolveVisionBrand,
  resolveVisionColor,
  resolveVisionModel,
  resolveVisionRegistrationNumber,
  resolveVisionVehicleType,
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

export function FieldVerificationSummary({
  result,
  onViewDetailed,
  onDownloadPdf,
}: FieldVerificationSummaryProps) {
  const navigate = useNavigate();
  const completed = result.status === "completed";
  const registrationNumber = resolveVisionRegistrationNumber(result);
  const verificationStatus = formatVerificationStatus(result.verification_result?.lookup_status);
  const challan = resolveChallanSummary(result);
  const failureMessage = result.failure_message?.trim() || null;
  const comparisonItems = result.attribute_comparison?.items ?? [];
  const hasRegistry = result.vehicle_information != null;

  return (
    <div className="animate-slide-up space-y-5">
      <Alert
        variant={completed ? "success" : "warning"}
        title={completed ? "Verification Complete" : "Verification Incomplete"}
      >
        {result.failed_stage ? (
          <p className="break-words text-sm">
            Failed at {WORKFLOW_STAGE_LABELS[result.failed_stage] ?? result.failed_stage}
            {failureMessage ? `: ${failureMessage}` : ""}
          </p>
        ) : result.status === "processing" ? (
          <p className="text-sm">
            The server returned a processing response instead of a finished investigation.
            Restart the backend and try again.
          </p>
        ) : failureMessage ? (
          <p className="text-sm">{failureMessage}</p>
        ) : !completed ? (
          <p className="text-sm">
            The investigation could not be completed. No registration number was detected.
          </p>
        ) : (
          <p className="text-sm">
            Field summary for <span className="font-mono font-semibold">{registrationNumber}</span>
          </p>
        )}
      </Alert>

      <Card
        title="Vision AI Observation"
        description="Gemini Vision output only — not registry data"
        icon={<FileSearch className="h-4 w-4" />}
        accent
      >
        <dl>
          <SummaryRow label="Registration Number" value={registrationNumber} />
          <SummaryRow label="Brand" value={resolveVisionBrand(result)} />
          <SummaryRow label="Model" value={resolveVisionModel(result)} />
          <SummaryRow label="Color" value={resolveVisionColor(result)} />
          <SummaryRow label="Vehicle Type" value={resolveVisionVehicleType(result)} />
          <SummaryRow
            label="Overall Confidence"
            value={formatConfidencePercent(result.vision_confidence)}
          />
          <SummaryRow
            label="Brand Confidence"
            value={formatConfidencePercent(result.vision_attributes?.brand_confidence)}
          />
          <SummaryRow
            label="Color Confidence"
            value={formatConfidencePercent(result.vision_attributes?.color_confidence)}
          />
          <SummaryRow
            label="Type Confidence"
            value={formatConfidencePercent(result.vision_attributes?.vehicle_type_confidence)}
          />
          <SummaryRow label="Explanation" value={result.vision_explanation?.trim() || "—"} />
        </dl>
      </Card>

      <Card title="Registry Verification" description="Official database record only">
        <dl>
          <SummaryRow label="Verification Status" value={verificationStatus} />
          <SummaryRow label="Owner Name" value={resolveOwnerName(result)} />
          {hasRegistry ? (
            <>
              <SummaryRow label="Brand (Make)" value={resolveRegistryMake(result)} />
              <SummaryRow label="Model" value={resolveRegistryModel(result)} />
              <SummaryRow label="Color" value={resolveRegistryColor(result)} />
              <SummaryRow label="Vehicle Type" value={resolveRegistryVehicleType(result)} />
            </>
          ) : (
            <SummaryRow
              label="Registry Record"
              value={result.verification_result?.message ?? "No matching vehicle record was found."}
            />
          )}
        </dl>
      </Card>

      {comparisonItems.length > 0 ? (
        <Card title="Attribute Comparison" description="Vision AI vs Registry">
          <div className="table-scroll overflow-x-auto rounded-xl border border-slate-200">
            <table className="min-w-full text-left text-sm">
              <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
                <tr>
                  <th className="px-3 py-2">Attribute</th>
                  <th className="px-3 py-2">Vision AI</th>
                  <th className="px-3 py-2">Registry</th>
                  <th className="px-3 py-2">Result</th>
                </tr>
              </thead>
              <tbody>
                {comparisonItems.map((item) => (
                  <tr key={item.attribute} className="border-t border-slate-100">
                    <td className="px-3 py-2 font-medium capitalize text-slate-800">{item.attribute}</td>
                    <td className="px-3 py-2 capitalize text-slate-700">{item.observed}</td>
                    <td className="px-3 py-2 capitalize text-slate-700">{item.registered ?? "—"}</td>
                    <td className="px-3 py-2 font-semibold">
                      {item.matches === true ? "MATCH" : item.matches === false ? "MISMATCH" : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      ) : null}

      <Card title="Investigation Summary" description="Risk and enforcement context">
        <dl>
          <SummaryRow
            label="Risk Level"
            value={(result.risk_level ?? "—").replaceAll("_", " ").toUpperCase()}
          />
          <SummaryRow
            label="Risk Score"
            value={result.risk_score != null ? `${formatRiskScore(result.risk_score)}/100` : "—"}
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
