import { getAuthenticatedApiData, postFormDataApi } from "@/services/api/httpClient";
import type { VehicleVerificationWorkflowResult, VisionProgress } from "@/types/api/workflow";

export const workflowService = {
  runVehicleVerification(
    vehicleImage: File,
    locationLabel?: string,
    correlationId?: string,
  ): Promise<VehicleVerificationWorkflowResult> {
    const formData = new FormData();
    formData.append("vehicle_image", vehicleImage);
    if (locationLabel) formData.append("location_label", locationLabel);
    const headers = correlationId ? { "X-Correlation-ID": correlationId } : undefined;
    return postFormDataApi<VehicleVerificationWorkflowResult>(
      "/v1/workflow/vehicle-verification",
      formData,
      headers,
    );
  },

  getVisionProgress(correlationId: string, signal?: AbortSignal): Promise<VisionProgress> {
    const query = new URLSearchParams({ correlation_id: correlationId });
    return getAuthenticatedApiData<VisionProgress>(
      `/v1/workflow/vision-progress?${query.toString()}`,
      signal ? { signal } : undefined,
    );
  },
};
