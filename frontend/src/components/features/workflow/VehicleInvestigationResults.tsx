import { FileSearch } from "lucide-react";

import { VehicleInvestigationResult } from "@/components/features/workflow/VehicleInvestigationResult";
import { Card } from "@/components/ui/Card";
import type { VehicleVerificationWorkflowResult } from "@/types/api/workflow";
import type { VehicleRegion } from "@/types/vehicleSelection";

interface VehicleInvestigationResultsProps {
  results: VehicleVerificationWorkflowResult[];
  vehicleImageUrl: string | null;
  regions: VehicleRegion[];
  thumbnails: Record<string, string>;
}

function resolveRegionForResult(
  result: VehicleVerificationWorkflowResult,
  regions: VehicleRegion[],
  index: number,
): VehicleRegion | undefined {
  if (result.vehicle_region_id) {
    return regions.find((region) => region.vehicle_id === result.vehicle_region_id);
  }
  return regions[index];
}

export function VehicleInvestigationResults({
  results,
  vehicleImageUrl,
  regions,
  thumbnails,
}: VehicleInvestigationResultsProps) {
  if (results.length === 0) {
    return null;
  }

  const multiVehicle = results.length > 1;

  return (
    <div className="space-y-6">
      {multiVehicle && (
        <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3">
          <p className="text-sm font-medium text-slate-900">
            Investigations: {results.length}
          </p>
          <p className="mt-1 text-sm text-slate-600">
            Each rectangle was cropped, analyzed, verified, and reported independently.
          </p>
        </div>
      )}

      {results.map((result, index) => {
        const region = resolveRegionForResult(result, regions, index);
        const thumbnailUrl = region ? thumbnails[region.vehicle_id] : undefined;
        const title = multiVehicle
          ? `Investigation Card ${index + 1}${
              result.registration_number ? ` — ${result.registration_number}` : ""
            }`
          : "Investigation Result";

        return (
          <Card
            key={result.workflow_id}
            title={title}
            description={
              region
                ? `${region.label}${region.vehicle_type ? ` · ${region.vehicle_type}` : ""}`
                : undefined
            }
            icon={<FileSearch className="h-4 w-4" />}
          >
            {thumbnailUrl && (
              <div className="mb-5 overflow-hidden rounded-xl border border-slate-200 bg-slate-950">
                <img
                  src={thumbnailUrl}
                  alt={region?.label ?? `Investigation ${index + 1}`}
                  className="mx-auto max-h-48 w-full object-contain"
                  draggable={false}
                />
              </div>
            )}
            <VehicleInvestigationResult
              result={result}
              vehicleImageUrl={thumbnailUrl ?? vehicleImageUrl}
            />
          </Card>
        );
      })}
    </div>
  );
}
