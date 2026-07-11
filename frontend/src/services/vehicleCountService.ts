import { postFormDataApi } from "@/services/api/httpClient";
import type { VisibleVehicleCountResponse } from "@/types/vehicleSelection";

export const vehicleCountService = {
  countVisibleVehicles(
    vehicleImage: File,
    signal?: AbortSignal,
  ): Promise<VisibleVehicleCountResponse> {
    const formData = new FormData();
    formData.append("vehicle_image", vehicleImage);
    return postFormDataApi<VisibleVehicleCountResponse>(
      "/v1/workflow/count-visible-vehicles",
      formData,
      undefined,
      signal,
    );
  },
};
