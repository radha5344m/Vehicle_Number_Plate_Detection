import type { VehicleRegion } from "@/types/vehicleSelection";

interface VehicleThumbnailCardProps {
  region: VehicleRegion;
  thumbnailUrl?: string;
  selected?: boolean;
  disabled?: boolean;
  readOnly?: boolean;
  registrationNumber?: string | null;
  onToggle?: () => void;
}

export function VehicleThumbnailCard({
  region,
  thumbnailUrl,
  selected = false,
  disabled = false,
  readOnly = false,
  registrationNumber,
  onToggle,
}: VehicleThumbnailCardProps) {
  const content = (
    <>
      <div className="relative aspect-[4/3] w-full bg-slate-900">
        {thumbnailUrl ? (
          <img
            src={thumbnailUrl}
            alt={region.label}
            className="h-full w-full object-cover"
            draggable={false}
          />
        ) : (
          <div className="flex h-full items-center justify-center text-xs text-slate-400">Loading…</div>
        )}
        {!readOnly && (
          <span
            className={`absolute left-2 top-2 rounded px-2 py-0.5 text-xs font-semibold ${
              selected ? "bg-brand text-white" : "bg-slate-800/90 text-slate-100"
            }`}
          >
            {selected ? "☑" : "☐"}
          </span>
        )}
      </div>
      <div className="space-y-1 px-3 py-2">
        <p className="text-sm font-semibold text-slate-900">{region.label}</p>
        {registrationNumber && (
          <p className="truncate text-xs font-medium text-brand">{registrationNumber}</p>
        )}
        {region.vehicle_type && (
          <p className="text-[10px] uppercase tracking-wide text-slate-500">{region.vehicle_type}</p>
        )}
      </div>
    </>
  );

  if (readOnly) {
    return (
      <div className="flex flex-col overflow-hidden rounded-xl border border-slate-200 bg-white shadow-soft">
        {content}
      </div>
    );
  }

  return (
    <button
      type="button"
      disabled={disabled}
      onClick={onToggle}
      className={`flex flex-col overflow-hidden rounded-xl border text-left transition-all ${
        selected
          ? "border-brand bg-brand/5 ring-2 ring-brand/30"
          : "border-slate-200 bg-white hover:border-slate-300 hover:shadow-soft"
      } ${disabled ? "cursor-not-allowed opacity-60" : "cursor-pointer"}`}
    >
      {content}
    </button>
  );
}
