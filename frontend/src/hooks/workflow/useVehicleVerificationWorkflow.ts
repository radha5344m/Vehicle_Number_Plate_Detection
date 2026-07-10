import { useCallback, useEffect, useRef, useState } from "react";
import { HttpError } from "@/services/api/httpClient";
import { workflowService } from "@/services/workflowService";
import type { VehicleVerificationWorkflowResult } from "@/types/api/workflow";

const VERIFYING_MESSAGE = "Verifying vehicle…";

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

interface UseVehicleVerificationWorkflowResult {
  run: (vehicleImage: File, locationLabel?: string) => Promise<void>;
  result: VehicleVerificationWorkflowResult | null;
  loading: boolean;
  isVerifying: boolean;
  error: string | null;
  loadingMessage: string | null;
  reset: () => void;
}

export function useVehicleVerificationWorkflow(): UseVehicleVerificationWorkflowResult {
  const [result, setResult] = useState<VehicleVerificationWorkflowResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const verificationActiveRef = useRef(false);
  const startRequestAbortRef = useRef<AbortController | null>(null);

  const reset = useCallback(() => {
    startRequestAbortRef.current?.abort();
    startRequestAbortRef.current = null;
    verificationActiveRef.current = false;
    setResult(null);
    setLoading(false);
    setError(null);
  }, []);

  useEffect(() => {
    return () => {
      startRequestAbortRef.current?.abort();
      verificationActiveRef.current = false;
    };
  }, []);

  const run = useCallback(async (vehicleImage: File, locationLabel?: string) => {
    if (verificationActiveRef.current) {
      return;
    }

    verificationActiveRef.current = true;
    startRequestAbortRef.current?.abort();
    const startAbort = new AbortController();
    startRequestAbortRef.current = startAbort;

    setResult(null);
    setError(null);
    setLoading(true);

    try {
      const data = await workflowService.startVehicleVerification(
        vehicleImage,
        locationLabel,
        startAbort.signal,
      );

      if (startAbort.signal.aborted) {
        return;
      }

      if (data.status === "processing") {
        throw new Error(
          "Backend returned a processing response. Restart the backend (python main.py) and try again.",
        );
      }

      setResult(normalizeWorkflowResult(data));
      if (data.status === "failed") {
        if (!data.failure_message && !data.registration_number) {
          setError(
            "Verification could not be completed. No registration number was detected.",
          );
        }
      } else if (data.status !== "completed" && !data.registration_number) {
        setError(
          data.failure_message ??
            "Verification could not be completed. No registration number was detected.",
        );
      }
    } catch (err) {
      if (startAbort.signal.aborted || (err instanceof DOMException && err.name === "AbortError")) {
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
      if (startRequestAbortRef.current === startAbort) {
        startRequestAbortRef.current = null;
      }
    }
  }, []);

  return {
    run,
    result,
    loading,
    isVerifying: loading,
    error,
    loadingMessage: loading ? VERIFYING_MESSAGE : null,
    reset,
  };
}
