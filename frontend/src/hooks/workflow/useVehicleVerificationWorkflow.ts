import { useState } from "react";
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

interface UseVehicleVerificationWorkflowResult {
  run: (vehicleImage: File, locationLabel?: string) => Promise<void>;
  result: VehicleVerificationWorkflowResult | null;
  loading: boolean;
  error: string | null;
  reset: () => void;
}

export function useVehicleVerificationWorkflow(): UseVehicleVerificationWorkflowResult {
  const [result, setResult] = useState<VehicleVerificationWorkflowResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function run(vehicleImage: File, locationLabel?: string) {
    setLoading(true);
    setError(null);
    try {
      const data = await workflowService.runVehicleVerification(vehicleImage, locationLabel);
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
      setLoading(false);
    }
  }

  function reset() {
    setResult(null);
    setError(null);
  }

  return { run, result, loading, error, reset };
}
