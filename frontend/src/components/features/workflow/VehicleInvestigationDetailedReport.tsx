import type { ReactNode } from "react";
import {
  ArrowLeft,
  BarChart3,
  ClipboardList,
  Download,
  FileSearch,
  Scale,
  ShieldAlert,
  ShieldCheck,
} from "lucide-react";

import { RiskLevelBadge } from "@/components/features/history/RiskLevelBadge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import type { RiskLevel } from "@/types/api/history";
import {
  WORKFLOW_STAGE_LABELS,
  type AttributeComparisonItem,
  type VehicleVerificationWorkflowResult,
} from "@/types/api/workflow";

interface VehicleInvestigationDetailedReportProps {
  result: VehicleVerificationWorkflowResult;
  vehicleImageUrl: string | null;
  onBack: () => void;
  onDownloadPdf: () => void;
}

function formatRiskScore(score: number | null): string {
  if (score == null) return "—";
  return `${Math.round(score * 100)}`;
}

function formatConfidence(value: number | null | undefined): string {
  if (value == null) return "—";
  return `${(value * 100).toFixed(0)}%`;
}

function orDash(value: string | null | undefined): string {
  const text = value?.toString().trim();
  return text ? text : "—";
}

function matchRate(items: AttributeComparisonItem[] | undefined): number {
  if (!items?.length) return 0;
  const matched = items.filter((item) => item.matches === true).length;
  return Math.round((matched / items.length) * 100);
}

function formatDuration(ms: number | null | undefined): string {
  if (ms == null) return "—";
  if (ms < 1000) return `${ms} ms`;
  return `${(ms / 1000).toFixed(2)} s`;
}

function ProgressBar({
  label,
  value,
  tone = "teal",
}: {
  label: string;
  value: number | null | undefined;
  tone?: "teal" | "blue" | "amber" | "red" | "slate";
}) {
  const pct = value == null ? 0 : Math.max(0, Math.min(100, Math.round(value * 100)));
  const tones: Record<string, string> = {
    teal: "bg-teal-600",
    blue: "bg-blue-600",
    amber: "bg-amber-500",
    red: "bg-red-600",
    slate: "bg-slate-500",
  };
  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-xs">
        <span className="font-medium text-slate-600">{label}</span>
        <span className="font-mono font-semibold text-slate-800">
          {value == null ? "—" : `${pct}%`}
        </span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-slate-200">
        <div className={`h-full rounded-full ${tones[tone]}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

function RiskGauge({ score, level }: { score: number | null; level: string | null }) {
  const tone =
    level === "critical" || level === "high" ? "red" : level === "medium" ? "amber" : "teal";
  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
      <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Risk Gauge</p>
      <div className="mt-2 flex items-end gap-3">
        <p className="font-mono text-4xl font-bold text-slate-900">
          {formatRiskScore(score)}
          <span className="text-base font-medium text-slate-400">/100</span>
        </p>
        {level ? <RiskLevelBadge level={level as RiskLevel} /> : null}
      </div>
      <div className="mt-3">
        <ProgressBar label="Risk Intensity" value={score} tone={tone} />
      </div>
    </div>
  );
}

function DetailRow({
  label,
  value,
  capitalize = false,
  mono = false,
}: {
  label: string;
  value: ReactNode;
  capitalize?: boolean;
  mono?: boolean;
}) {
  return (
    <div className="flex items-start justify-between gap-4 border-b border-slate-100 py-2.5 last:border-b-0">
      <dt className="text-sm text-slate-500">{label}</dt>
      <dd
        className={`max-w-[65%] text-right text-sm font-semibold text-slate-800 ${capitalize ? "capitalize" : ""} ${
          mono ? "font-mono" : ""
        }`}
      >
        {value}
      </dd>
    </div>
  );
}

function SectionCard({
  number,
  title,
  description,
  icon,
  children,
  accent = false,
}: {
  number: number;
  title: string;
  description?: string;
  icon?: ReactNode;
  children: ReactNode;
  accent?: boolean;
}) {
  return (
    <Card title={`${number}. ${title}`} description={description} icon={icon} accent={accent}>
      {children}
    </Card>
  );
}

function composeUiReasoning(result: VehicleVerificationWorkflowResult): string {
  const parts: string[] = [];
  const plate = result.registration_number ?? "UNKNOWN";
  const confidence = result.vision_confidence;

  if (confidence != null) {
    parts.push(
      `Vision AI extracted registration number ${plate} with overall confidence ${(confidence * 100).toFixed(0)}%.`,
    );
  } else {
    parts.push(`Investigation examined registration number ${plate}.`);
  }
  if (result.vision_explanation) {
    parts.push(`Vision model rationale: ${result.vision_explanation}`);
  }

  const lookup = result.verification_result?.lookup_status;
  if (lookup === "found") {
    parts.push(`Registry verification located a matching vehicle record for ${plate}.`);
  } else if (lookup === "not_found") {
    parts.push(`Registry verification did not locate an authoritative record for ${plate}.`);
  } else if (result.verification_result?.message) {
    parts.push(`Registry verification outcome: ${result.verification_result.message}`);
  }

  const comparison = result.attribute_comparison;
  if (comparison?.items?.length) {
    const rate = matchRate(comparison.items);
    const mismatched = comparison.items.filter((item) => item.matches === false);
    parts.push(
      `Attribute comparison covered ${comparison.items.length} fields with a match rate of ${rate}%.`,
    );
    if (mismatched.length) {
      parts.push(
        `Material mismatches: ${mismatched
          .map(
            (item) =>
              `${item.attribute}: observed '${item.observed}' vs registered '${item.registered ?? "—"}'`,
          )
          .join("; ")}.`,
      );
    }
  }

  if (result.risk_level != null) {
    parts.push(
      `The risk engine assigned level ${result.risk_level.toUpperCase()} with score ${formatRiskScore(result.risk_score)}/100.`,
    );
  }
  if (result.risk_explanation) {
    parts.push(`Risk explanation: ${result.risk_explanation}`);
  }
  if (result.risk_signals?.length) {
    parts.push(
      `Contributing risk signals — ${result.risk_signals
        .map((signal) => `${signal.name} (weight ${signal.weight.toFixed(2)}): ${signal.detail}`)
        .join("; ")}.`,
    );
  }
  if (result.investigation_summary) {
    parts.push(`Investigation summary: ${result.investigation_summary}`);
  }
  if (result.recommendation) {
    parts.push(`Officer recommendation from the risk assessment policy: ${result.recommendation}`);
  }
  return parts.join(" ");
}

export function VehicleInvestigationDetailedReport({
  result,
  vehicleImageUrl,
  onBack,
  onDownloadPdf,
}: VehicleInvestigationDetailedReportProps) {
  const vehicle = result.vehicle_information;
  const attributes = result.vision_attributes;
  const comparison = result.attribute_comparison;
  const registrationNumber = result.registration_number ?? "—";
  const confidence = result.vision_confidence;
  const attrMatchPct = matchRate(comparison?.items);
  const reasoning = composeUiReasoning(result);
  const caseRef = `INV-${(result.scan_id ?? result.workflow_id).slice(0, 8).toUpperCase()}-${registrationNumber}`;
  const steps = result.steps ?? [];
  const successSteps = steps.filter((step) => step.status === "success").length;

  return (
    <div className="animate-slide-up min-w-0 space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-center sm:justify-between">
        <Button
          className="w-full sm:w-auto"
          variant="secondary"
          icon={<ArrowLeft className="h-4 w-4" />}
          onClick={onBack}
        >
          Back to Field Summary
        </Button>
        {result.report_download_url ? (
          <Button className="w-full sm:w-auto" icon={<Download className="h-4 w-4" />} onClick={onDownloadPdf}>
            Download PDF
          </Button>
        ) : null}
      </div>

      <SectionCard
        number={1}
        title="Case Information"
        description="Investigating officer and subject vehicle"
        icon={<ClipboardList className="h-4 w-4" />}
      >
        <dl>
          <DetailRow label="Case Reference" value={caseRef} mono />
          <DetailRow label="Registration Number" value={registrationNumber} mono />
          <DetailRow label="Workflow ID" value={result.workflow_id} mono />
          <DetailRow label="Scan ID" value={orDash(result.scan_id)} mono />
          <DetailRow label="Completed At" value={new Date(result.completed_at).toLocaleString()} />
          <DetailRow label="Classification" value="RESTRICTED — LAW ENFORCEMENT USE" />
        </dl>
      </SectionCard>

      <SectionCard
        number={2}
        title="Investigation Metadata"
        description="System identifiers and verification context"
        icon={<FileSearch className="h-4 w-4" />}
      >
        <dl>
          <DetailRow
            label="Lookup Status"
            value={orDash(result.verification_result?.lookup_status).toUpperCase()}
          />
          <DetailRow label="Verification Message" value={orDash(result.verification_result?.message)} />
          <DetailRow label="Total Duration" value={formatDuration(result.total_duration_ms)} />
          <DetailRow label="Report ID" value={orDash(result.report_id)} mono />
        </dl>
      </SectionCard>

      <section className="grid gap-4 lg:grid-cols-2">
        <SectionCard number={3} title="Vehicle Evidence" description="Uploaded photographic exhibit">
          {vehicleImageUrl ? (
            <img
              src={vehicleImageUrl}
              alt="Uploaded vehicle evidence"
              className="max-h-80 w-full rounded-xl border border-slate-200 object-contain"
            />
          ) : (
            <p className="text-sm text-slate-500">No image preview available.</p>
          )}
        </SectionCard>

        <SectionCard
          number={4}
          title="AI Vision Analysis"
          description="Structured Google Gemini Vision output"
        >
          <dl>
            <DetailRow label="Registration" value={registrationNumber} mono />
            <DetailRow label="Brand" value={orDash(attributes?.brand)} capitalize />
            <DetailRow label="Model" value={orDash(result.vehicle_model)} capitalize />
            <DetailRow label="Color" value={orDash(attributes?.color)} capitalize />
            <DetailRow label="Vehicle Type" value={orDash(attributes?.vehicle_type)} capitalize />
            <DetailRow label="Confidence" value={formatConfidence(confidence)} />
            <DetailRow label="Explanation" value={orDash(result.vision_explanation)} />
          </dl>
          <div className="mt-4 space-y-3">
            <ProgressBar label="Overall Vision Confidence" value={confidence} tone="teal" />
            <ProgressBar label="Color Confidence" value={attributes?.color_confidence} tone="blue" />
            <ProgressBar
              label="Type Confidence"
              value={attributes?.vehicle_type_confidence}
              tone="blue"
            />
            <ProgressBar label="Brand Confidence" value={attributes?.brand_confidence} tone="blue" />
          </div>
        </SectionCard>
      </section>

      <SectionCard number={5} title="Registry Verification" description="Authoritative vehicle registry result">
        {vehicle ? (
          <dl>
            <DetailRow label="Owner" value={orDash(vehicle.registered_owner)} />
            <DetailRow label="Make" value={orDash(vehicle.make)} />
            <DetailRow label="Model" value={orDash(vehicle.model)} />
            <DetailRow label="Year" value={vehicle.year != null ? String(vehicle.year) : "—"} />
            <DetailRow label="Color" value={orDash(vehicle.color)} capitalize />
            <DetailRow label="Vehicle Type" value={orDash(vehicle.vehicle_type)} capitalize />
            <DetailRow label="Registration Status" value={orDash(vehicle.registration_status)} />
            <DetailRow label="Jurisdiction" value={orDash(vehicle.jurisdiction)} />
          </dl>
        ) : (
          <p className="text-sm text-amber-800">
            {result.verification_result?.message ?? "No matching vehicle record was found."}
          </p>
        )}
      </SectionCard>

      <SectionCard
        number={6}
        title="Vehicle Attribute Comparison"
        description="Observed AI attributes versus registry"
      >
        <div className="mb-4">
          <ProgressBar
            label="Attribute Match Rate"
            value={attrMatchPct / 100}
            tone={attrMatchPct >= 70 ? "teal" : attrMatchPct >= 40 ? "amber" : "red"}
          />
          <p className="mt-2 text-sm text-slate-600">
            Overall:{" "}
            <span className="font-semibold text-slate-900">
              {comparison?.overall_match === true
                ? "MATCH"
                : comparison?.overall_match === false
                  ? "MISMATCH"
                  : "INCONCLUSIVE"}
            </span>
          </p>
        </div>
        {comparison?.items?.length ? (
          <div className="table-scroll overflow-x-auto rounded-xl border border-slate-200">
            <table className="min-w-full text-left text-sm">
              <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
                <tr>
                  <th className="px-3 py-2">Attribute</th>
                  <th className="px-3 py-2">Observed</th>
                  <th className="px-3 py-2">Registered</th>
                  <th className="px-3 py-2">Result</th>
                  <th className="px-3 py-2">Conf.</th>
                </tr>
              </thead>
              <tbody>
                {comparison.items.map((item) => (
                  <tr key={item.attribute} className="border-t border-slate-100">
                    <td className="px-3 py-2 font-medium capitalize text-slate-800">{item.attribute}</td>
                    <td className="px-3 py-2 capitalize text-slate-700">{item.observed}</td>
                    <td className="px-3 py-2 capitalize text-slate-700">{orDash(item.registered)}</td>
                    <td className="px-3 py-2 font-semibold">
                      {item.matches === true ? "MATCH" : item.matches === false ? "MISMATCH" : "—"}
                    </td>
                    <td className="px-3 py-2 font-mono text-slate-600">
                      {formatConfidence(item.confidence)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-sm text-slate-500">Attribute comparison data was not available.</p>
        )}
      </SectionCard>

      <SectionCard
        number={7}
        title="Risk Analytics"
        description="Policy-driven risk scoring and contributing signals"
        icon={<ShieldAlert className="h-4 w-4" />}
        accent
      >
        <RiskGauge score={result.risk_score} level={result.risk_level} />
        {(result.risk_signals?.length ?? 0) > 0 && (
          <div className="mt-4 space-y-2">
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Risk Signals</p>
            {result.risk_signals?.map((signal) => (
              <div
                key={`${signal.name}-${signal.detail}`}
                className="rounded-lg border border-slate-200 bg-white px-3 py-2"
              >
                <div className="flex items-center justify-between gap-3">
                  <p className="text-sm font-semibold text-slate-800">{signal.name}</p>
                  <span className="font-mono text-xs text-slate-500">w={signal.weight.toFixed(2)}</span>
                </div>
                <p className="mt-1 text-sm text-slate-600">{signal.detail}</p>
              </div>
            ))}
          </div>
        )}
      </SectionCard>

      <SectionCard
        number={8}
        title="AI Reasoning"
        description="Dynamically composed from Vision, registry, comparison, and risk outputs"
        icon={<Scale className="h-4 w-4" />}
      >
        <p className="text-sm leading-relaxed text-slate-700">{reasoning}</p>
      </SectionCard>

      <SectionCard number={9} title="Investigation Timeline" description="Ordered processing stages for this case">
        {steps.length ? (
          <ol className="space-y-3">
            {steps.map((step, index) => (
              <li
                key={`${step.stage}-${index}`}
                className="flex gap-3 rounded-xl border border-slate-200 bg-slate-50 px-3 py-2"
              >
                <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-slate-800 text-xs font-bold text-white">
                  {index + 1}
                </span>
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <p className="text-sm font-semibold text-slate-900">
                      {WORKFLOW_STAGE_LABELS[step.stage] ?? step.stage}
                    </p>
                    <span
                      className={`rounded-full px-2 py-0.5 text-[10px] font-bold uppercase ${
                        step.status === "success"
                          ? "bg-emerald-100 text-emerald-800"
                          : "bg-amber-100 text-amber-800"
                      }`}
                    >
                      {step.status}
                    </span>
                  </div>
                  <p className="mt-0.5 text-sm text-slate-600">{step.message}</p>
                  <p className="mt-0.5 font-mono text-xs text-slate-400">{formatDuration(step.duration_ms)}</p>
                </div>
              </li>
            ))}
          </ol>
        ) : (
          <p className="text-sm text-slate-500">No timeline steps recorded.</p>
        )}
      </SectionCard>

      <section className="grid gap-4 lg:grid-cols-2">
        <SectionCard
          number={10}
          title="Investigation Statistics"
          description="Quantitative summary of this investigation"
          icon={<BarChart3 className="h-4 w-4" />}
        >
          <dl>
            <DetailRow label="Stages Executed" value={String(steps.length)} />
            <DetailRow label="Successful Stages" value={String(successSteps)} />
            <DetailRow label="Total Duration" value={formatDuration(result.total_duration_ms)} />
            <DetailRow label="Vision Confidence" value={formatConfidence(confidence)} />
            <DetailRow label="Attribute Match Rate" value={`${attrMatchPct}%`} />
            <DetailRow label="Risk Score" value={`${formatRiskScore(result.risk_score)}/100`} />
            <DetailRow label="Risk Signals" value={String(result.risk_signals?.length ?? 0)} />
          </dl>
        </SectionCard>

        <SectionCard
          number={11}
          title="Digital Evidence"
          description="Chain-of-custody summary for photographic evidence"
        >
          <dl>
            <DetailRow label="Evidence Type" value="Vehicle photograph" />
            <DetailRow label="Custody" value="Authenticated officer session" />
            <DetailRow label="Workflow Link" value={result.workflow_id} mono />
            <DetailRow label="Scan Link" value={orDash(result.scan_id)} mono />
            <DetailRow label="Integrity" value="Image SHA-256 embedded in downloadable PDF" />
          </dl>
        </SectionCard>
      </section>

      <SectionCard
        number={12}
        title="Final Investigation Conclusion"
        description="Synthesized case disposition"
        icon={<ShieldCheck className="h-4 w-4" />}
        accent
      >
        <p className="text-sm leading-relaxed text-slate-700">
          {result.investigation_summary ??
            `Subject registration ${registrationNumber} was investigated with risk level ${(result.risk_level ?? "unknown").toUpperCase()} (${formatRiskScore(result.risk_score)}/100). Registry status: ${result.verification_result?.lookup_status ?? "unavailable"}. Attribute match rate: ${attrMatchPct}%.`}
        </p>
      </SectionCard>
    </div>
  );
}
