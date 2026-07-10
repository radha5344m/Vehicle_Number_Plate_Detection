import { postFormDataApi } from "@/services/api/httpClient";

import type { VehicleVerificationWorkflowResult } from "@/types/api/workflow";
import type { VehicleRegion } from "@/types/vehicleSelection";
import { toSelectedRegionsPayload } from "@/types/vehicleSelection";

export const workflowService = {
  startVehicleVerification(
    vehicleImage: File,
    locationLabel?: string,
    signal?: AbortSignal,
    selectedRegions?: VehicleRegion[],
  ): Promise<VehicleVerificationWorkflowResult> {
    const formData = new FormData();
    formData.append("vehicle_image", vehicleImage);
    if (locationLabel) formData.append("location_label", locationLabel);
    if (selectedRegions && selectedRegions.length > 0) {
      formData.append("selected_regions", JSON.stringify(toSelectedRegionsPayload(selectedRegions)));
    }

    return postFormDataApi<VehicleVerificationWorkflowResult>(
      "/v1/workflow/vehicle-verification",
      formData,
      undefined,
      signal,
    );
  },
};
