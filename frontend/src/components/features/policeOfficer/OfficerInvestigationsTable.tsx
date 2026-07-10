import { Download, Eye } from "lucide-react";

import { RiskLevelBadge } from "@/components/features/history/RiskLevelBadge";
import { Button } from "@/components/ui/Button";
import type { InvestigationReportListItem } from "@/types/api/investigationReports";

interface Props {
  items: InvestigationReportListItem[];
  onDownloadReport: (item: InvestigationReportListItem) => void;
  onViewDetails?: (item: InvestigationReportListItem) => void;
}

export function OfficerInvestigationsTable({
  items,
  onDownloadReport,
  onViewDetails,
}: Props) {
  if (items.length === 0) {
    return (
      <p className="rounded-2xl border border-dashed border-slate-300 bg-white px-4 py-12 text-center text-sm text-slate-400">
        No investigations match the selected filters.
      </p>
    );
  }

  return (
    <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-soft">
      <div className="table-scroll overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead className="border-b border-slate-200 bg-slate-50 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
            <tr>
              <th className="px-4 py-3.5">Date</th>
              <th className="px-4 py-3.5">Registration</th>
              <th className="px-4 py-3.5">Vehicle Type</th>
              <th className="px-4 py-3.5">Risk</th>
              <th className="px-4 py-3.5">Verification</th>
              <th className="px-4 py-3.5">AI Confidence</th>
              <th className="px-4 py-3.5">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {items.map((item) => (
              <tr key={item.investigation_id} className="text-slate-700 transition-colors hover:bg-slate-50">
                <td className="px-4 py-3.5">{new Date(item.scanned_at).toLocaleString()}</td>
                <td className="px-4 py-3.5 font-mono font-semibold text-slate-900">
                  {item.registration_number}
                </td>
                <td className="px-4 py-3.5">{item.vehicle_type ?? "—"}</td>
                <td className="px-4 py-3.5">
                  <div className="space-y-1">
                    <RiskLevelBadge level={item.risk_level} />
                    <p className="font-mono text-xs text-slate-500">
                      {Math.round(item.risk_score * 100)}/100
                    </p>
                  </div>
                </td>
                <td className="px-4 py-3.5 uppercase text-slate-500">
                  {item.verification_status ?? "—"}
                </td>
                <td className="px-4 py-3.5 font-mono text-slate-500">
                  {item.ai_confidence != null ? `${Math.round(item.ai_confidence * 100)}%` : "—"}
                </td>
                <td className="px-4 py-3.5">
                  <div className="flex flex-wrap gap-2">
                    <Button
                      size="sm"
                      variant="secondary"
                      icon={<Eye className="h-4 w-4" />}
                      onClick={() => onViewDetails?.(item)}
                      disabled={!onViewDetails}
                    >
                      Details
                    </Button>
                    {item.report_download_url && (
                      <Button
                        size="sm"
                        variant="secondary"
                        icon={<Download className="h-4 w-4" />}
                        onClick={() => onDownloadReport(item)}
                      >
                        PDF
                      </Button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
