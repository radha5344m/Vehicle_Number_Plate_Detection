import { Download, Eye, Printer } from "lucide-react";

import { RiskLevelBadge } from "@/components/features/history/RiskLevelBadge";
import { Button } from "@/components/ui/Button";
import type { InvestigationReportListItem } from "@/types/api/investigationReports";

function formatDateTime(value: string): { date: string; time: string } {
  const date = new Date(value);
  return {
    date: date.toLocaleDateString(),
    time: date.toLocaleTimeString(),
  };
}

interface Props {
  items: InvestigationReportListItem[];
  onDownloadReport: (item: InvestigationReportListItem) => void;
  onViewDetails?: (item: InvestigationReportListItem) => void;
  onPrintReport?: (item: InvestigationReportListItem) => void;
}

export function InvestigationReportsTable({
  items,
  onDownloadReport,
  onViewDetails,
  onPrintReport,
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
              <th className="px-4 py-3.5">Time</th>
              <th className="px-4 py-3.5">Investigation ID</th>
              <th className="px-4 py-3.5">Registration</th>
              <th className="px-4 py-3.5">Owner</th>
              <th className="px-4 py-3.5">Vehicle</th>
              <th className="px-4 py-3.5">Brand</th>
              <th className="px-4 py-3.5">Model</th>
              <th className="px-4 py-3.5">Officer</th>
              <th className="px-4 py-3.5">Police Station</th>
              <th className="px-4 py-3.5">District</th>
              <th className="px-4 py-3.5">Risk Score</th>
              <th className="px-4 py-3.5">Risk Level</th>
              <th className="px-4 py-3.5">Investigation Status</th>
              <th className="px-4 py-3.5">Verification</th>
              <th className="px-4 py-3.5">AI Confidence</th>
              <th className="px-4 py-3.5">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {items.map((item) => {
              const { date, time } = formatDateTime(item.scanned_at);
              return (
                <tr
                  key={item.investigation_id}
                  className="text-slate-700 transition-colors hover:bg-slate-50"
                >
                  <td className="px-4 py-3.5">{date}</td>
                  <td className="px-4 py-3.5">{time}</td>
                  <td className="px-4 py-3.5 font-mono text-xs">{item.investigation_id}</td>
                  <td className="px-4 py-3.5 font-mono font-semibold text-slate-900">
                    {item.registration_number}
                  </td>
                  <td className="px-4 py-3.5">{item.owner ?? "�"}</td>
                  <td className="px-4 py-3.5">{item.vehicle ?? "�"}</td>
                  <td className="px-4 py-3.5">{item.brand ?? "�"}</td>
                  <td className="px-4 py-3.5">{item.model ?? "�"}</td>
                  <td className="px-4 py-3.5">{item.officer_name}</td>
                  <td className="px-4 py-3.5">{item.police_station ?? item.station_name ?? "�"}</td>
                  <td className="px-4 py-3.5">{item.district ?? "�"}</td>
                  <td className="px-4 py-3.5 font-mono">
                    {Math.round(item.risk_score * 100)}/100
                  </td>
                  <td className="px-4 py-3.5">
                    <RiskLevelBadge level={item.risk_level} />
                  </td>
                  <td className="px-4 py-3.5 uppercase text-slate-500">
                    {item.investigation_status}
                  </td>
                  <td className="px-4 py-3.5 uppercase text-slate-500">
                    {item.verification_status ?? "�"}
                  </td>
                  <td className="px-4 py-3.5 font-mono text-slate-500">
                    {item.ai_confidence != null ? `${Math.round(item.ai_confidence * 100)}%` : "�"}
                  </td>
                  <td className="px-4 py-3.5">
                    <div className="flex flex-wrap gap-2">
                      {onViewDetails ? (
                        <Button
                          size="sm"
                          variant="secondary"
                          icon={<Eye className="h-4 w-4" />}
                          onClick={() => onViewDetails(item)}
                        >
                          Details
                        </Button>
                      ) : null}
                      {item.report_download_url ? (
                        <Button
                          size="sm"
                          variant="secondary"
                          icon={<Download className="h-4 w-4" />}
                          onClick={() => onDownloadReport(item)}
                        >
                          PDF
                        </Button>
                      ) : null}
                      {onPrintReport ? (
                        <Button
                          size="sm"
                          variant="ghost"
                          icon={<Printer className="h-4 w-4" />}
                          onClick={() => onPrintReport(item)}
                        >
                          Print
                        </Button>
                      ) : null}
                      {!onViewDetails && !item.report_download_url && !onPrintReport ? (
                        <span className="text-slate-400">�</span>
                      ) : null}
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
