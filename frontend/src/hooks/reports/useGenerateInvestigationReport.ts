import { useState } from "react";
import { reportService } from "@/services/reportService";
import type {
  GenerateInvestigationReportInput,
  InvestigationReportResult,
} from "@/types/api/report";

interface UseGenerateInvestigationReportResult {
  generate: (vehicleImage: File, payload: GenerateInvestigationReportInput) => Promise<void>;
  download: () => Promise<void>;
  result: InvestigationReportResult | null;
  loading: boolean;
  error: string | null;
  reset: () => void;
}

export function useGenerateInvestigationReport(): UseGenerateInvestigationReportResult {
  const [result, setResult] = useState<InvestigationReportResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function generate(vehicleImage: File, payload: GenerateInvestigationReportInput) {
    setLoading(true);
    setError(null);
    try {
      const data = await reportService.generateInvestigationReport(vehicleImage, payload);
      setResult(data);
    } catch {
      setError("Failed to generate investigation report");
      throw new Error("Failed to generate investigation report");
    } finally {
      setLoading(false);
    }
  }

  async function download() {
    if (!result) return;
    await reportService.downloadReport(
      result.download_url,
      `investigation-report-${result.report_id}.pdf`,
    );
  }

  function reset() {
    setResult(null);
    setError(null);
  }

  return { generate, download, result, loading, error, reset };
}
