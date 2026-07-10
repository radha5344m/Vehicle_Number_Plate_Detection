import { postFormDataApi } from "@/services/api/httpClient";
import type { VehicleDetectionResponse } from "@/types/vehicleSelection";

export const vehicleDetectionService = {
  detectVehicles(vehicleImage: File, signal?: AbortSignal): Promise<VehicleDetectionResponse> {
    const formData = new FormData();
    formData.append("vehicle_image", vehicleImage);
    return postFormDataApi<VehicleDetectionResponse>(
      "/v1/workflow/detect-vehicles",
      formData,
      undefined,
      signal,
    );
  },
};
