import { useCallback, useEffect, useRef, useState } from "react";
import { Plus, ShieldCheck, Trash2 } from "lucide-react";

import { VehicleBoundingBox } from "@/components/features/workflow/VehicleBoundingBox";
import { Button } from "@/components/ui/Button";
import {
  clampRegion,
  createManualRegion,
  relabelRegions,
  type VehicleRegion,
} from "@/types/vehicleSelection";

interface MultiRectangleSelectorProps {
  imageUrl: string;
  regions: VehicleRegion[];
  selectedRegionId: string | null;
  disabled?: boolean;
  verifying?: boolean;
  onRegionsChange: (regions: VehicleRegion[]) => void;
  onSelectedRegionChange: (regionId: string | null) => void;
  onVerify: () => void;
}

export function MultiRectangleSelector({
  imageUrl,
  regions,
  selectedRegionId,
  disabled = false,
  verifying = false,
  onRegionsChange,
  onSelectedRegionChange,
  onVerify,
}: MultiRectangleSelectorProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [containerSize, setContainerSize] = useState({ width: 0, height: 0 });

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const updateSize = () => {
      const rect = container.getBoundingClientRect();
      setContainerSize({
        width: Math.round(rect.width),
        height: Math.round(rect.height),
      });
    };

    updateSize();
    const observer = new ResizeObserver(updateSize);
    observer.observe(container);
    return () => observer.disconnect();
  }, [imageUrl]);

  const updateRegion = useCallback(
    (regionId: string, nextRegion: VehicleRegion) => {
      onRegionsChange(
        relabelRegions(
          regions.map((region) =>
            region.vehicle_id === regionId ? clampRegion(nextRegion) : region,
          ),
        ),
      );
    },
    [onRegionsChange, regions],
  );

  const handleAddRectangle = () => {
    if (disabled || verifying) return;
    const nextRegion = createManualRegion(regions.length);
    const nextRegions = relabelRegions([...regions, nextRegion]);
    onRegionsChange(nextRegions);
    onSelectedRegionChange(nextRegion.vehicle_id);
  };

  const handleDeleteSelected = () => {
    if (disabled || verifying || !selectedRegionId || regions.length <= 1) return;
    const remaining = regions.filter((region) => region.vehicle_id !== selectedRegionId);
    const nextRegions = relabelRegions(remaining);
    onRegionsChange(nextRegions);
    onSelectedRegionChange(nextRegions[0]?.vehicle_id ?? null);
  };

  const ready = containerSize.width > 0 && containerSize.height > 0;

  return (
    <div className="space-y-4">
      <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3">
        <p className="text-sm font-medium text-slate-900">Rectangles: {regions.length}</p>
        <p className="mt-1 text-sm text-slate-600">
          Draw one rectangle per vehicle. Each rectangle is cropped and investigated independently.
        </p>
      </div>

      <div
        ref={containerRef}
        className="relative overflow-hidden overscroll-none rounded-2xl border border-slate-200 bg-slate-950 shadow-soft touch-none"
        style={{ touchAction: "none" }}
      >
        <img
          src={imageUrl}
          alt="Uploaded vehicle scene"
          className="block h-auto w-full select-none"
          draggable={false}
        />
        {ready && (
          <div className="absolute inset-0 touch-none" style={{ touchAction: "none" }}>
            {regions.map((region, index) => {
              const selected = region.vehicle_id === selectedRegionId;
              return (
                <VehicleBoundingBox
                  key={region.vehicle_id}
                  region={region}
                  selected={selected}
                  disabled={disabled || verifying}
                  containerWidth={containerSize.width}
                  containerHeight={containerSize.height}
                  zIndex={selected ? 20 + index : 10 + index}
                  onRegionChange={(nextRegion) => updateRegion(region.vehicle_id, nextRegion)}
                  onSelect={() => onSelectedRegionChange(region.vehicle_id)}
                />
              );
            })}
          </div>
        )}
      </div>

      <div className="flex flex-wrap gap-3">
        <Button
          type="button"
          variant="secondary"
          size="sm"
          icon={<Plus className="h-4 w-4" />}
          disabled={disabled || verifying}
          onClick={handleAddRectangle}
        >
          Add Rectangle
        </Button>
        <Button
          type="button"
          variant="secondary"
          size="sm"
          icon={<Trash2 className="h-4 w-4" />}
          disabled={disabled || verifying || !selectedRegionId || regions.length <= 1}
          onClick={handleDeleteSelected}
        >
          Delete Rectangle
        </Button>
      </div>

      <Button
        type="button"
        disabled={disabled || verifying || regions.length === 0}
        loading={verifying}
        icon={<ShieldCheck className="h-4 w-4" />}
        size="lg"
        className="w-full min-h-12 sm:w-auto"
        onClick={onVerify}
      >
        Verify {regions.length === 1 ? "Vehicle" : "Vehicles"}
      </Button>
    </div>
  );
}
