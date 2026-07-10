import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import type { StationItem } from "@/types/api/stations";

function statusVariant(status: string): "success" | "warning" | "default" {
  if (status === "active") return "success";
  if (status === "inactive") return "warning";
  return "default";
}

interface Props {
  items: StationItem[];
  onEdit: (station: StationItem) => void;
  onToggleStatus: (station: StationItem) => void;
  onDelete: (station: StationItem) => void;
  canManage?: boolean;
}

export function StationsTable({
  items,
  onEdit,
  onToggleStatus,
  onDelete,
  canManage = true,
}: Props) {
  if (items.length === 0) {
    return <p className="rounded-2xl border border-dashed border-slate-300 bg-white px-4 py-12 text-center text-sm text-slate-400">No stations match the selected filters.</p>;
  }

  return (
    <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-soft">
      <div className="table-scroll overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead className="border-b border-slate-200 bg-slate-50 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
            <tr>
              <th className="px-4 py-3.5">Station Code</th>
              <th className="px-4 py-3.5">Station Name</th>
              <th className="px-4 py-3.5">District</th>
              <th className="px-4 py-3.5">State</th>
              <th className="px-4 py-3.5">Station Type</th>
              <th className="px-4 py-3.5">Phone</th>
              <th className="px-4 py-3.5">Status</th>
              <th className="px-4 py-3.5">Created Date</th>
              <th className="px-4 py-3.5">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {items.map((station) => (
              <tr key={station.station_id} className="text-slate-700 transition-colors hover:bg-slate-50">
                <td className="px-4 py-3.5 font-mono">{station.station_code}</td>
                <td className="px-4 py-3.5">
                  <div className="font-medium text-slate-900">{station.station_name}</div>
                  <div className="text-xs text-slate-500">{station.email ?? "No email"}</div>
                </td>
                <td className="px-4 py-3.5">{station.district}</td>
                <td className="px-4 py-3.5">{station.state}</td>
                <td className="px-4 py-3.5"><Badge variant="info">{station.station_type}</Badge></td>
                <td className="px-4 py-3.5 text-slate-500">{station.phone_number ?? "-"}</td>
                <td className="px-4 py-3.5"><Badge variant={statusVariant(station.status)}>{station.status}</Badge></td>
                <td className="px-4 py-3.5 text-slate-500">{new Date(station.created_at).toLocaleDateString()}</td>
                <td className="px-4 py-3.5">
                  {canManage ? (
                    <div className="flex flex-wrap gap-2">
                      <Button size="sm" variant="secondary" onClick={() => onEdit(station)}>Edit</Button>
                      <Button size="sm" variant="secondary" onClick={() => onToggleStatus(station)}>{station.status === "active" ? "Deactivate" : "Activate"}</Button>
                      <Button size="sm" variant="danger" onClick={() => onDelete(station)}>Delete</Button>
                    </div>
                  ) : (
                    <span className="text-xs text-slate-400">No actions available</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
