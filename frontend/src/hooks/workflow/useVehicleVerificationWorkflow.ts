import { useCallback, useEffect, useRef, useState } from "react";
import { HttpError } from "@/services/api/httpClient";
import { vehicleDetectionService } from "@/services/vehicleDetectionService";
import { workflowService } from "@/services/workflowService";
import type { VehicleVerificationWorkflowResult } from "@/types/api/workflow";
import {
  createManualRegion,
  detectedVehicleToRegion,
  relabelRegions,
  type VehicleRegion,
} from "@/types/vehicleSelection";

const DETECTING_MESSAGE = "Detecting vehicles in the image…";
const AUTO_VERIFYING_MESSAGE = "Starting automatic investigation…";
const MANUAL_VERIFYING_MESSAGE = "Running independent investigations for each rectangle…";

export type SmartWorkflowMode = "idle" | "detecting" | "auto" | "manual";

function normalizeWorkflowResult(
  data: VehicleVerificationWorkflowResult,
): VehicleVerificationWorkflowResult {
  return {
    ...data,
    steps: data.steps ?? [],
    risk_signals: data.risk_signals ?? [],
    attribute_comparison: data.attribute_comparison
      ? { ...data.attribute_comparison, items: data.attribute_comparison.items ?? [] }
      : null,
  };
}

function extractInvestigationResults(
  data: VehicleVerificationWorkflowResult,
): VehicleVerificationWorkflowResult[] {
  const normalized = normalizeWorkflowResult(data);
  if (normalized.investigations && normalized.investigations.length > 0) {
    return normalized.investigations.map((item) => normalizeWorkflowResult(item));
  }
  return [normalized];
}

interface UseVehicleVerificationWorkflowResult {
  startSmartWorkflow: (vehicleImage: File, locationLabel?: string) => Promise<void>;
  verifyRectangles: (
    vehicleImage: File,
    regions: VehicleRegion[],
    locationLabel?: string,
  ) => Promise<void>;
  results: VehicleVerificationWorkflowResult[];
  loading: boolean;
  isVerifying: boolean;
  isDetecting: boolean;
  error: string | null;
  detectionError: string | null;
  loadingMessage: string | null;
  workflowMode: SmartWorkflowMode;
  detectedCount: number;
  regions: VehicleRegion[];
  selectedRegionId: string | null;
  setRegions: (regions: VehicleRegion[]) => void;
  setSelectedRegionId: (regionId: string | null) => void;
  reset: () => void;
}

export function useVehicleVerificationWorkflow(): UseVehicleVerificationWorkflowResult {
  const [results, setResults] = useState<VehicleVerificationWorkflowResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [isDetecting, setIsDetecting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [detectionError, setDetectionError] = useState<string | null>(null);
  const [workflowMode, setWorkflowMode] = useState<SmartWorkflowMode>("idle");
  const [detectedCount, setDetectedCount] = useState(0);
  const [regions, setRegions] = useState<VehicleRegion[]>([]);
  const [selectedRegionId, setSelectedRegionId] = useState<string | null>(null);

  const workflowActiveRef = useRef(false);
  const requestAbortRef = useRef<AbortController | null>(null);

  const reset = useCallback(() => {
    requestAbortRef.current?.abort();
    requestAbortRef.current = null;
    workflowActiveRef.current = false;
    setResults([]);
    setLoading(false);
    setIsDetecting(false);
    setError(null);
    setDetectionError(null);
    setWorkflowMode("idle");
    setDetectedCount(0);
    setRegions([]);
    setSelectedRegionId(null);
  }, []);

  useEffect(() => {
    return () => {
      requestAbortRef.current?.abort();
      workflowActiveRef.current = false;
    };
  }, []);

  const runVerification = useCallback(
    async (
      vehicleImage: File,
      rectangleRegions: VehicleRegion[],
      signal: AbortSignal,
      locationLabel?: string,
    ) => {
      const data = await workflowService.startVehicleVerification(
        vehicleImage,
        locationLabel,
        signal,
        rectangleRegions,
      );

      if (signal.aborted) {
        return;
      }

      if (data.status === "processing") {
        throw new Error(
          "Backend returned a processing response. Restart the backend (python main.py) and try again.",
        );
      }

      const investigations = extractInvestigationResults(data);
      setResults(investigations);

      const successCount = investigations.filter((item) => item.status === "completed").length;
      if (successCount === 0) {
        const firstFailure = investigations.find((item) => item.failure_message)?.failure_message;
        setError(firstFailure ?? "Investigation could not be completed for any vehicle.");
        return;
      }

      setError(null);
    },
    [],
  );

  const verifyRectangles = useCallback(
    async (vehicleImage: File, rectangleRegions: VehicleRegion[], locationLabel?: string) => {
      if (workflowActiveRef.current || rectangleRegions.length === 0) {
        return;
      }

      workflowActiveRef.current = true;
      requestAbortRef.current?.abort();
      const abort = new AbortController();
      requestAbortRef.current = abort;

      setResults([]);
      setError(null);
      setLoading(true);
      setWorkflowMode("manual");

      try {
        await runVerification(vehicleImage, rectangleRegions, abort.signal, locationLabel);
      } catch (err) {
        if (abort.signal.aborted || (err instanceof DOMException && err.name === "AbortError")) {
          return;
        }

        const message =
          err instanceof HttpError
            ? err.message
            : err instanceof TypeError
              ? "Cannot reach the backend — ensure it is running on port 8080 (python main.py)."
              : err instanceof Error && err.message
                ? err.message
                : "Vehicle verification failed. Please try again.";
        setError(message);
        throw new Error(message);
      } finally {
        workflowActiveRef.current = false;
        setLoading(false);
        if (requestAbortRef.current === abort) {
          requestAbortRef.current = null;
        }
      }
    },
    [runVerification],
  );

  const startSmartWorkflow = useCallback(
    async (vehicleImage: File, locationLabel?: string) => {
      if (workflowActiveRef.current) {
        return;
      }

      workflowActiveRef.current = true;
      requestAbortRef.current?.abort();
      const abort = new AbortController();
      requestAbortRef.current = abort;

      setResults([]);
      setError(null);
      setDetectionError(null);
      setRegions([]);
      setSelectedRegionId(null);
      setDetectedCount(0);
      setIsDetecting(true);
      setLoading(false);
      setWorkflowMode("detecting");

      let detectedRegions: VehicleRegion[] = [];

      try {
        const detection = await vehicleDetectionService.detectVehicles(vehicleImage, abort.signal);
        if (abort.signal.aborted) {
          return;
        }

        detectedRegions = relabelRegions(
          detection.vehicles.map((vehicle, index) => detectedVehicleToRegion(vehicle, index)),
        );
        setDetectedCount(detectedRegions.length);
        setRegions(detectedRegions);
        setIsDetecting(false);

        if (detectedRegions.length === 1) {
          setWorkflowMode("auto");
          setLoading(true);
          await runVerification(vehicleImage, detectedRegions, abort.signal, locationLabel);
          return;
        }

        if (detectedRegions.length > 1) {
          setWorkflowMode("manual");
          setSelectedRegionId(detectedRegions[0]?.vehicle_id ?? null);
          return;
        }

        const fallbackRegion = createManualRegion(0);
        const fallbackRegions = relabelRegions([fallbackRegion]);
        setRegions(fallbackRegions);
        setSelectedRegionId(fallbackRegion.vehicle_id);
        setWorkflowMode("manual");
        const message =
          "No vehicles were auto-detected. Draw rectangles around each vehicle you want to investigate.";
        setDetectionError(message);
      } catch (err) {
        if (abort.signal.aborted || (err instanceof DOMException && err.name === "AbortError")) {
          return;
        }

        const message =
          err instanceof HttpError
            ? err.status === 404
              ? "Vehicle detection endpoint not found. Restart the backend with python main.py to load the latest API routes."
              : err.message
            : err instanceof TypeError
              ? "Cannot reach the backend — ensure it is running on port 8080 (python main.py)."
              : err instanceof Error && err.message
                ? err.message
                : "Vehicle detection failed. Please try again.";

        const fallbackRegion = createManualRegion(0);
        const fallbackRegions = relabelRegions([fallbackRegion]);
        setRegions(fallbackRegions);
        setSelectedRegionId(fallbackRegion.vehicle_id);
        setWorkflowMode("manual");
        setDetectionError(message);
      } finally {
        workflowActiveRef.current = false;
        setIsDetecting(false);
        setLoading(false);
        if (requestAbortRef.current === abort) {
          requestAbortRef.current = null;
        }
      }
    },
    [runVerification],
  );

  const loadingMessage = loading
    ? workflowMode === "auto"
      ? AUTO_VERIFYING_MESSAGE
      : MANUAL_VERIFYING_MESSAGE
    : isDetecting
      ? DETECTING_MESSAGE
      : null;

  return {
    startSmartWorkflow,
    verifyRectangles,
    results,
    loading,
    isVerifying: loading,
    isDetecting,
    error,
    detectionError,
    loadingMessage,
    workflowMode,
    detectedCount,
    regions,
    selectedRegionId,
    setRegions,
    setSelectedRegionId,
    reset,
  };
}
