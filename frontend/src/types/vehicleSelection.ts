export interface DetectedVehicle {
  vehicle_id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  confidence: number;
  vehicle_type: string;
}

export interface VehicleRegion {
  vehicle_id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  confidence?: number;
  vehicle_type?: string;
  label: string;
}

export interface VehicleDetectionResponse {
  vehicles: DetectedVehicle[];
  visible_plate_count: number;
}

export interface VisibleVehicleType {
  type: string;
}

export interface VisibleVehicleCountResponse {
  vehicle_count: number;
  vehicles: VisibleVehicleType[];
}

export function detectedVehicleToRegion(
  vehicle: DetectedVehicle,
  index: number,
): VehicleRegion {
  return {
    vehicle_id: vehicle.vehicle_id,
    x: vehicle.x,
    y: vehicle.y,
    width: vehicle.width,
    height: vehicle.height,
    confidence: vehicle.confidence,
    vehicle_type: vehicle.vehicle_type,
    label: `Vehicle ${index + 1}`,
  };
}

export function createManualRegion(index: number): VehicleRegion {
  return {
    vehicle_id: crypto.randomUUID(),
    x: 0.15 + (index % 3) * 0.08,
    y: 0.15 + Math.floor(index / 3) * 0.08,
    width: 0.35,
    height: 0.45,
    label: `Rectangle ${index + 1}`,
  };
}

export function clampRegion(region: VehicleRegion): VehicleRegion {
  const minSize = 0.04;
  const width = Math.max(minSize, Math.min(1, region.width));
  const height = Math.max(minSize, Math.min(1, region.height));
  const x = Math.max(0, Math.min(1 - width, region.x));
  const y = Math.max(0, Math.min(1 - height, region.y));
  return { ...region, x, y, width, height };
}

export function relabelRegions(regions: VehicleRegion[]): VehicleRegion[] {
  return regions.map((region, index) => ({
    ...region,
    label: `Rectangle ${index + 1}`,
  }));
}

export function toSelectedRegionsPayload(regions: VehicleRegion[]) {
  return regions.map(({ vehicle_id, x, y, width, height }) => ({
    vehicle_id,
    x,
    y,
    width,
    height,
  }));
}

/** Minimum bounding-box size in pixels (used by react-rnd). */
export const MIN_BOX_PX = 36;

export function regionToPixels(
  region: VehicleRegion,
  containerWidth: number,
  containerHeight: number,
): { x: number; y: number; width: number; height: number } {
  return {
    x: region.x * containerWidth,
    y: region.y * containerHeight,
    width: Math.max(MIN_BOX_PX, region.width * containerWidth),
    height: Math.max(MIN_BOX_PX, region.height * containerHeight),
  };
}

export function pixelsToRegion(
  region: VehicleRegion,
  x: number,
  y: number,
  width: number,
  height: number,
  containerWidth: number,
  containerHeight: number,
): VehicleRegion {
  return clampRegion({
    ...region,
    x: x / containerWidth,
    y: y / containerHeight,
    width: width / containerWidth,
    height: height / containerHeight,
  });
}
