import { useEffect, useRef, useState } from "react";
import { HttpError } from "@/services/api/httpClient";
import { workflowService } from "@/services/workflowService";
import { isAuthenticated } from "@/stores/authStore";
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
  const pollAbortRef = useRef<AbortController | null>(null);
  const pollIntervalRef = useRef<number | null>(null);

  function stopProgressPolling() {
    pollAbortRef.current?.abort();
    pollAbortRef.current = null;
    if (pollIntervalRef.current !== null) {
      window.clearInterval(pollIntervalRef.current);
      pollIntervalRef.current = null;
    }
  }

  function startProgressPolling(correlationId: string) {
    stopProgressPolling();

    if (!isAuthenticated()) {
      return;
    }

    const controller = new AbortController();
    pollAbortRef.current = controller;

    async function pollProgress() {
      if (controller.signal.aborted || !isAuthenticated()) {
        return;
      }

      try {
        const progress = await workflowService.getVisionProgress(
          correlationId,
          controller.signal,
        );
        if (controller.signal.aborted) {
          return;
        }

        if (progress.phase !== "idle" && progress.message) {
          setProgressMessage(progress.message);
        }

        if (progress.phase === "completed" || progress.phase === "failed") {
          stopProgressPolling();
        }
      } catch (err) {
        if (controller.signal.aborted) {
          return;
        }
        if (err instanceof HttpError && (err.status === 401 || err.code === "AUTH_MISSING")) {
          stopProgressPolling();
        }
      }
    }

    void pollProgress();
    pollIntervalRef.current = window.setInterval(() => {
      void pollProgress();
    }, 1000);
  }

  useEffect(() => {
    return () => {
      stopProgressPolling();
    };
  }, []);

  async function run(vehicleImage: File, locationLabel?: string) {
    const correlationId = createCorrelationId();
    setLoading(true);
    setError(null);
    setProgressMessage(null);
    startProgressPolling(correlationId);

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
      stopProgressPolling();
      setProgressMessage(null);
      setLoading(false);
    }
  }

  function reset() {
    stopProgressPolling();
    setResult(null);
    setError(null);
    setProgressMessage(null);
  }

  return { run, result, loading, error, progressMessage, reset };
}
