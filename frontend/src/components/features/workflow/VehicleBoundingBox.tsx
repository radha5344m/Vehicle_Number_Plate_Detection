import type { CSSProperties } from "react";
import { Rnd } from "react-rnd";

import {
  MIN_BOX_PX,
  pixelsToRegion,
  regionToPixels,
  type VehicleRegion,
} from "@/types/vehicleSelection";

const RESIZE_ALL = {
  top: true,
  right: true,
  bottom: true,
  left: true,
  topRight: true,
  bottomRight: true,
  bottomLeft: true,
  topLeft: true,
} as const;

const RESIZE_NONE = {
  top: false,
  right: false,
  bottom: false,
  left: false,
  topRight: false,
  bottomRight: false,
  bottomLeft: false,
  topLeft: false,
} as const;

const HANDLE_STYLE: CSSProperties = {
  width: 10,
  height: 10,
  borderRadius: "9999px",
  border: "2px solid white",
  backgroundColor: "var(--color-brand, #2563eb)",
  boxShadow: "0 1px 3px rgba(0,0,0,0.35)",
};

interface VehicleBoundingBoxProps {
  region: VehicleRegion;
  selected: boolean;
  disabled?: boolean;
  containerWidth: number;
  containerHeight: number;
  zIndex: number;
  onRegionChange: (region: VehicleRegion) => void;
  onSelect: () => void;
}

export function VehicleBoundingBox({
  region,
  selected,
  disabled = false,
  containerWidth,
  containerHeight,
  zIndex,
  onRegionChange,
  onSelect,
}: VehicleBoundingBoxProps) {
  const { x, y, width, height } = regionToPixels(region, containerWidth, containerHeight);

  const applyPixels = (nextX: number, nextY: number, nextW: number, nextH: number) => {
    onRegionChange(
      pixelsToRegion(region, nextX, nextY, nextW, nextH, containerWidth, containerHeight),
    );
  };

  return (
    <Rnd
      bounds="parent"
      size={{ width, height }}
      position={{ x, y }}
      minWidth={MIN_BOX_PX}
      minHeight={MIN_BOX_PX}
      disableDragging={disabled}
      enableResizing={selected && !disabled ? RESIZE_ALL : RESIZE_NONE}
      resizeHandleStyles={{
        top: HANDLE_STYLE,
        right: HANDLE_STYLE,
        bottom: HANDLE_STYLE,
        left: HANDLE_STYLE,
        topRight: HANDLE_STYLE,
        bottomRight: HANDLE_STYLE,
        bottomLeft: HANDLE_STYLE,
        topLeft: HANDLE_STYLE,
      }}
      style={{ zIndex }}
      className={`box-border touch-none ${
        selected
          ? "border-2 border-brand bg-brand/15 ring-2 ring-brand/40"
          : "border-2 border-slate-400 bg-slate-400/10 ring-2 ring-slate-300/50"
      } ${disabled ? "cursor-not-allowed" : "cursor-move"}`}
      onDragStart={() => {
        if (!disabled && !selected) {
          onSelect();
        }
      }}
      onDrag={(_event, data) => {
        applyPixels(data.x, data.y, width, height);
      }}
      onDragStop={(_event, data) => {
        applyPixels(data.x, data.y, width, height);
      }}
      onResize={(_event, _direction, ref, _delta, position) => {
        applyPixels(position.x, position.y, ref.offsetWidth, ref.offsetHeight);
      }}
      onResizeStop={(_event, _direction, ref, _delta, position) => {
        applyPixels(position.x, position.y, ref.offsetWidth, ref.offsetHeight);
      }}
      onMouseDown={(event) => {
        event.stopPropagation();
      }}
    >
      <button
        type="button"
        disabled={disabled}
        className={`absolute left-1 top-1 rounded px-2 py-0.5 text-xs font-semibold ${
          selected ? "bg-brand text-white" : "bg-slate-700 text-slate-100"
        } ${disabled ? "cursor-not-allowed" : "cursor-pointer"}`}
        onClick={(event) => {
          event.stopPropagation();
          if (!disabled) {
            onSelect();
          }
        }}
      >
        {region.label}
      </button>
    </Rnd>
  );
}
