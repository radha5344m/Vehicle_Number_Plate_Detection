import { Spinner } from "@/components/ui/Spinner";

interface SmartVerificationStatusProps {
  detecting: boolean;
  verifying: boolean;
  detectedCount: number;
}

export function SmartVerificationStatus({
  detecting,
  verifying,
  detectedCount,
}: SmartVerificationStatusProps) {
  return (
    <div className="space-y-4">
      <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3">
        <p className="text-sm font-medium text-slate-900">1 Vehicle Detected</p>
        <p className="mt-1 text-sm text-slate-600">
          {detecting
            ? "Analyzing the scene…"
            : verifying
              ? "Starting Automatic Investigation…"
              : "Preparing automatic investigation…"}
        </p>
      </div>
      {(detecting || verifying) && (
        <div className="flex items-center gap-3 rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-600">
          <Spinner size="sm" />
          {detecting
            ? "Detecting vehicles in the uploaded image"
            : "Cropping vehicle, running Vision AI, registry verification, and report generation"}
        </div>
      )}
      {detectedCount === 1 && !detecting && !verifying && (
        <p className="text-xs text-slate-500">
          Single-vehicle scenes are verified automatically without rectangle selection.
        </p>
      )}
    </div>
  );
}
