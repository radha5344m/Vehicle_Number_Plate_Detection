import { useCallback, useEffect, useRef, useState } from "react";
import { HttpError } from "@/services/api/httpClient";
import { workflowService } from "@/services/workflowService";
import type { VehicleVerificationWorkflowResult } from "@/types/api/workflow";
import {
  createManualRegion,
  relabelRegions,
  type VehicleRegion,
} from "@/types/vehicleSelection";

const VERIFYING_MESSAGE = "Running independent investigations for each rectangle…";

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
  verifyRectangles: (
    vehicleImage: File,
    regions: VehicleRegion[],
    locationLabel?: string,
  ) => Promise<void>;
  prepareImage: () => void;
  results: VehicleVerificationWorkflowResult[];
  loading: boolean;
  isVerifying: boolean;
  error: string | null;
  loadingMessage: string | null;
  regions: VehicleRegion[];
  selectedRegionId: string | null;
  setRegions: (regions: VehicleRegion[]) => void;
  setSelectedRegionId: (regionId: string | null) => void;
  reset: () => void;
}

export function useVehicleVerificationWorkflow(): UseVehicleVerificationWorkflowResult {
  const [results, setResults] = useState<VehicleVerificationWorkflowResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [regions, setRegions] = useState<VehicleRegion[]>([]);
  const [selectedRegionId, setSelectedRegionId] = useState<string | null>(null);

  const verificationActiveRef = useRef(false);
  const requestAbortRef = useRef<AbortController | null>(null);

  const reset = useCallback(() => {
    requestAbortRef.current?.abort();
    requestAbortRef.current = null;
    verificationActiveRef.current = false;
    setResults([]);
    setLoading(false);
    setError(null);
    setRegions([]);
    setSelectedRegionId(null);
  }, []);

  const prepareImage = useCallback(() => {
    const initialRegion = createManualRegion(0);
    const nextRegions = relabelRegions([initialRegion]);
    setRegions(nextRegions);
    setSelectedRegionId(initialRegion.vehicle_id);
    setResults([]);
    setError(null);
  }, []);

  useEffect(() => {
    return () => {
      requestAbortRef.current?.abort();
      verificationActiveRef.current = false;
    };
  }, []);

  const verifyRectangles = useCallback(
    async (vehicleImage: File, rectangleRegions: VehicleRegion[], locationLabel?: string) => {
      if (verificationActiveRef.current || rectangleRegions.length === 0) {
        return;
      }

      verificationActiveRef.current = true;
      requestAbortRef.current?.abort();
      const abort = new AbortController();
      requestAbortRef.current = abort;

      setResults([]);
      setError(null);
      setLoading(true);

      try {
        const data = await workflowService.startVehicleVerification(
          vehicleImage,
          locationLabel,
          abort.signal,
          rectangleRegions,
        );

        if (abort.signal.aborted) {
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
          setError(
            firstFailure ?? "Investigation could not be completed for any rectangle.",
          );
          return;
        }

        setError(null);
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
        verificationActiveRef.current = false;
        setLoading(false);
        if (requestAbortRef.current === abort) {
          requestAbortRef.current = null;
        }
      }
    },
    [],
  );

  return {
    verifyRectangles,
    prepareImage,
    results,
    loading,
    isVerifying: loading,
    error,
    loadingMessage: loading ? VERIFYING_MESSAGE : null,
    regions,
    selectedRegionId,
    setRegions,
    setSelectedRegionId,
    reset,
  };
}
