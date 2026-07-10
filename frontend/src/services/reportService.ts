import { env } from "@/config/env";
import { getAccessToken } from "@/stores/authStore";
import type { ApiResponse } from "@/types/api/common";
import type {
  GenerateInvestigationReportInput,
  InvestigationReportResult,
} from "@/types/api/report";

async function postFormData<T>(path: string, formData: FormData): Promise<T> {
  const base = env.apiBaseUrl.replace(/\/$/, "");
  const token = getAccessToken();
  const headers: Record<string, string> = {};
  if (token) headers.Authorization = `Bearer ${token}`;

  const response = await fetch(`${base}${path}`, {
    method: "POST",
    headers,
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }

  const envelope = (await response.json()) as ApiResponse<T>;
  return envelope.data;
}

export const reportService = {
  generateInvestigationReport(
    vehicleImage: File,
    payload: GenerateInvestigationReportInput,
  ): Promise<InvestigationReportResult> {
    const formData = new FormData();
    formData.append("vehicle_image", vehicleImage);
    formData.append("payload", JSON.stringify(payload));
    return postFormData<InvestigationReportResult>("/v1/reports/investigation", formData);
  },

  async downloadReport(downloadUrl: string, filename: string): Promise<void> {
    const base = env.apiBaseUrl.replace(/\/$/, "");
    const token = getAccessToken();
    const headers: Record<string, string> = {};
    if (token) headers.Authorization = `Bearer ${token}`;

    const response = await fetch(`${base}${downloadUrl}`, { headers });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const blob = await response.blob();
    const objectUrl = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = objectUrl;
    anchor.download = filename;
    anchor.click();
    URL.revokeObjectURL(objectUrl);
  },
};
