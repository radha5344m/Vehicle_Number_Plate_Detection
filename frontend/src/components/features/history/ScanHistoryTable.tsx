import type { ScanHistoryItem } from "@/types/api/history";
import { RiskLevelBadge } from "@/components/features/history/RiskLevelBadge";

interface ScanHistoryTableProps {
  items: ScanHistoryItem[];
}

function formatDate(value: string): string {
  return new Date(value).toLocaleString();
}

export function ScanHistoryTable({ items }: ScanHistoryTableProps) {
  if (items.length === 0) {
    return (
      <p className="rounded-2xl border border-dashed border-slate-300 bg-white px-4 py-12 text-center text-sm text-slate-400">
        No scans match the selected filters.
      </p>
    );
  }

  return (
    <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-soft">
      <div className="table-scroll overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead className="border-b border-slate-200 bg-slate-50 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
            <tr>
              <th className="px-4 py-3.5">Vehicle Number</th>
              <th className="px-4 py-3.5">Officer</th>
              <th className="px-4 py-3.5">Risk</th>
              <th className="px-4 py-3.5">Score</th>
              <th className="px-4 py-3.5">Location</th>
              <th className="px-4 py-3.5">Scanned At</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {items.map((item) => (
              <tr key={item.scan_id} className="text-slate-700 transition-colors hover:bg-slate-50">
                <td className="px-4 py-3.5 font-mono font-semibold text-slate-900">
                  {item.plate_text}
                </td>
                <td className="px-4 py-3.5">{item.officer_name}</td>
                <td className="px-4 py-3.5">
                  <RiskLevelBadge level={item.risk_level} />
                </td>
                <td className="px-4 py-3.5 font-mono">{item.risk_score.toFixed(2)}</td>
                <td className="px-4 py-3.5 text-slate-500">{item.location_label ?? "—"}</td>
                <td className="px-4 py-3.5 text-slate-500">{formatDate(item.scanned_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
