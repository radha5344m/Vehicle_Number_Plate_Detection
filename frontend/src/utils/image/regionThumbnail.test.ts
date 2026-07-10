import { describe, expect, it } from "vitest";

import type { VehicleRegion } from "@/types/vehicleSelection";
import { regionToCropRect, THUMBNAIL_PADDING_PX } from "@/utils/image/regionThumbnail";

const sampleRegion: VehicleRegion = {
  vehicle_id: "vehicle-1",
  x: 0.1,
  y: 0.2,
  width: 0.3,
  height: 0.4,
  label: "Vehicle 1",
};

describe("regionToCropRect", () => {
  it("applies padding and clamps to image bounds", () => {
    const rect = regionToCropRect(sampleRegion, 1000, 800, THUMBNAIL_PADDING_PX);

    expect(rect.x).toBe(Math.max(0, 100 - THUMBNAIL_PADDING_PX));
    expect(rect.y).toBe(Math.max(0, 160 - THUMBNAIL_PADDING_PX));
    expect(rect.width).toBeGreaterThan(0);
    expect(rect.height).toBeGreaterThan(0);
    expect(rect.x + rect.width).toBeLessThanOrEqual(1000);
    expect(rect.y + rect.height).toBeLessThanOrEqual(800);
  });
});
