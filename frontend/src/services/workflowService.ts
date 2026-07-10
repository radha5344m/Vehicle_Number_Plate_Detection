import { postFormDataApi } from "@/services/api/httpClient";
import type { VehicleVerificationWorkflowResult } from "@/types/api/workflow";

export const workflowService = {
  runVehicleVerification(
    vehicleImage: File,
    locationLabel?: string,
  ): Promise<VehicleVerificationWorkflowResult> {
    const formData = new FormData();
    formData.append("vehicle_image", vehicleImage);
    if (locationLabel) formData.append("location_label", locationLabel);
    return postFormDataApi<VehicleVerificationWorkflowResult>(
      "/v1/workflow/vehicle-verification",
      formData,
    );
  },
};
