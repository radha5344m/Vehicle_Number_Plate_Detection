import { useEffect, useMemo, useState } from "react";

import type { VehicleRegion } from "@/types/vehicleSelection";
import { cropRegionToDataUrl } from "@/utils/image/regionThumbnail";

function buildRegionKey(regions: VehicleRegion[]): string {
  return regions
    .map((region) => `${region.vehicle_id}:${region.x}:${region.y}:${region.width}:${region.height}`)
    .join("|");
}

export function useVehicleRegionThumbnails(
  imageUrl: string | null,
  regions: VehicleRegion[],
): Record<string, string> {
  const [thumbnails, setThumbnails] = useState<Record<string, string>>({});
  const regionKey = useMemo(() => buildRegionKey(regions), [regions]);

  useEffect(() => {
    if (!imageUrl || regions.length === 0) {
      setThumbnails({});
      return;
    }

    let cancelled = false;
    const image = new Image();
    image.onload = () => {
      if (cancelled) {
        return;
      }
      const next: Record<string, string> = {};
      for (const region of regions) {
        next[region.vehicle_id] = cropRegionToDataUrl(image, region);
      }
      setThumbnails(next);
    };
    image.src = imageUrl;

    return () => {
      cancelled = true;
      image.onload = null;
    };
  }, [imageUrl, regionKey, regions]);

  return thumbnails;
}
