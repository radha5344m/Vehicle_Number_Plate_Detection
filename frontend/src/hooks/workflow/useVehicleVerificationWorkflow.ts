import { useEffect, useRef, useState } from "react";
import { HttpError } from "@/services/api/httpClient";
import { workflowService } from "@/services/workflowService";
import type { VehicleVerificationWorkflowResult } from "@/types/api/workflow";

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

function createCorrelationId(): string {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return `workflow-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

interface UseVehicleVerificationWorkflowResult {
  run: (vehicleImage: File, locationLabel?: string) => Promise<void>;
  result: VehicleVerificationWorkflowResult | null;
  loading: boolean;
  error: string | null;
  progressMessage: string | null;
  reset: () => void;
}

export function useVehicleVerificationWorkflow(): UseVehicleVerificationWorkflowResult {
  const [result, setResult] = useState<VehicleVerificationWorkflowResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [progressMessage, setProgressMessage] = useState<string | null>(null);
  const activeCorrelationId = useRef<string | null>(null);

  useEffect(() => {
    if (!loading || !activeCorrelationId.current) {
      return;
    }

    let cancelled = false;
    const correlationId = activeCorrelationId.current;

    async function pollProgress() {
      try {
        const progress = await workflowService.getVisionProgress(correlationId);
        if (cancelled || !progress.message) return;
        if (progress.phase !== "idle") {
          setProgressMessage(progress.message);
        }
      } catch {
        // Progress polling is best-effort while the workflow request is in flight.
      }
    }

    void pollProgress();
    const interval = window.setInterval(() => {
      void pollProgress();
    }, 1000);

    return () => {
      cancelled = true;
      window.clearInterval(interval);
    };
  }, [loading]);

  async function run(vehicleImage: File, locationLabel?: string) {
    const correlationId = createCorrelationId();
    activeCorrelationId.current = correlationId;
    setLoading(true);
    setError(null);
    setProgressMessage(null);
    try {
      const data = await workflowService.runVehicleVerification(
        vehicleImage,
        locationLabel,
        correlationId,
      );
      setResult(normalizeWorkflowResult(data));
    } catch (err) {
      const message =
        err instanceof HttpError
          ? err.message
          : err instanceof TypeError
            ? "Cannot reach the backend — ensure it is running on port 8080 (python main.py)."
            : "Workflow failed — ensure you are logged in and the backend is running.";
      setError(message);
      throw new Error(message);
    } finally {
      activeCorrelationId.current = null;
      setProgressMessage(null);
      setLoading(false);
    }
  }

  function reset() {
    setResult(null);
    setError(null);
    setProgressMessage(null);
  }

  return { run, result, loading, error, progressMessage, reset };
}
