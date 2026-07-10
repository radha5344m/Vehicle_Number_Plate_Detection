import type { VehicleRegion } from "@/types/vehicleSelection";

/** Matches backend crop padding (10–20px range). */
export const THUMBNAIL_PADDING_PX = 15;

export interface CropRect {
  x: number;
  y: number;
  width: number;
  height: number;
}

export function regionToCropRect(
  region: VehicleRegion,
  imageWidth: number,
  imageHeight: number,
  paddingPx = THUMBNAIL_PADDING_PX,
): CropRect {
  const x = Math.max(0, Math.round(region.x * imageWidth - paddingPx));
  const y = Math.max(0, Math.round(region.y * imageHeight - paddingPx));
  const right = Math.min(
    imageWidth,
    Math.round((region.x + region.width) * imageWidth + paddingPx),
  );
  const bottom = Math.min(
    imageHeight,
    Math.round((region.y + region.height) * imageHeight + paddingPx),
  );
  return {
    x,
    y,
    width: Math.max(1, right - x),
    height: Math.max(1, bottom - y),
  };
}

export function cropRegionToDataUrl(
  image: HTMLImageElement,
  region: VehicleRegion,
  maxEdge = 160,
  paddingPx = THUMBNAIL_PADDING_PX,
): string {
  const { x, y, width, height } = regionToCropRect(
    region,
    image.naturalWidth,
    image.naturalHeight,
    paddingPx,
  );

  const canvas = document.createElement("canvas");
  const scale = Math.min(1, maxEdge / Math.max(width, height));
  canvas.width = Math.max(1, Math.round(width * scale));
  canvas.height = Math.max(1, Math.round(height * scale));

  const context = canvas.getContext("2d");
  if (!context) {
    return "";
  }

  context.drawImage(image, x, y, width, height, 0, 0, canvas.width, canvas.height);
  return canvas.toDataURL("image/jpeg", 0.88);
}
