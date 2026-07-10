import { useState } from "react";

import { FieldVerificationSummary } from "@/components/features/workflow/FieldVerificationSummary";
import { VehicleInvestigationDetailedReport } from "@/components/features/workflow/VehicleInvestigationDetailedReport";
import { reportService } from "@/services/reportService";
import type { VehicleVerificationWorkflowResult } from "@/types/api/workflow";

interface VehicleInvestigationResultProps {
  result: VehicleVerificationWorkflowResult;
  vehicleImageUrl: string | null;
  onReset?: () => void;
}

export function VehicleInvestigationResult({
  result,
  vehicleImageUrl,
}: VehicleInvestigationResultProps) {
  const [showDetailed, setShowDetailed] = useState(false);

  async function handleDownloadReport() {
    if (!result.report_download_url) return;
    const filename = `investigation-${result.report_id ?? result.workflow_id}.pdf`;
    await reportService.downloadReport(result.report_download_url, filename);
  }

  if (showDetailed) {
    return (
      <VehicleInvestigationDetailedReport
        result={result}
        vehicleImageUrl={vehicleImageUrl}
        onBack={() => setShowDetailed(false)}
        onDownloadPdf={() => void handleDownloadReport()}
      />
    );
  }

  return (
    <FieldVerificationSummary
      result={result}
      onViewDetailed={() => setShowDetailed(true)}
      onDownloadPdf={() => void handleDownloadReport()}
    />
  );
}
