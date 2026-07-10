import { useCallback, useEffect, useState } from "react";
import { ShieldCheck } from "lucide-react";

import { LiveCameraCapture } from "@/components/features/workflow/LiveCameraCapture";
import {
  VerificationMethodSelector,
  type VerificationMethod,
} from "@/components/features/workflow/VerificationMethodSelector";
import { MultiRectangleSelector } from "@/components/features/workflow/MultiRectangleSelector";
import { SmartVerificationStatus } from "@/components/features/workflow/SmartVerificationStatus";
import { VehicleInvestigationResults } from "@/components/features/workflow/VehicleInvestigationResults";
import { ImageUploadZone } from "@/components/features/upload/ImageUploadZone";
import { AiProcessingProgress } from "@/components/ui/AiProcessingProgress";
import { Alert } from "@/components/ui/Alert";
import { Card } from "@/components/ui/Card";
import { PageHeader } from "@/components/ui/PageHeader";
import { useToast } from "@/components/ui/Toast";
import { useVehicleVerificationWorkflow } from "@/hooks/workflow/useVehicleVerificationWorkflow";
import { useVehicleRegionThumbnails } from "@/hooks/workflow/useVehicleRegionThumbnails";
import { AppLayout } from "@/layouts/AppLayout";

export function VehicleVerificationWorkflowPage() {
  const toast = useToast();
  const {
    startSmartWorkflow,
    verifyRectangles,
    results,
    loading,
    isVerifying,
    isDetecting,
    error,
    detectionError,
    loadingMessage,
    workflowMode,
    detectedCount,
    regions,
    selectedRegionId,
    setRegions,
    setSelectedRegionId,
    reset,
  } = useVehicleVerificationWorkflow();
  const [method, setMethod] = useState<VerificationMethod | null>(null);
  const [vehicleImage, setVehicleImage] = useState<File | null>(null);
  const [vehicleImageUrl, setVehicleImageUrl] = useState<string | null>(null);
  const [cameraSessionKey, setCameraSessionKey] = useState(0);
  const [workflowStarted, setWorkflowStarted] = useState(false);

  useEffect(() => {
    if (error) {
      toast.error(error, "Verification Failed");
      return;
    }
    if (results.length === 1 && results[0]?.status === "completed") {
      toast.success(
        `Registration ${results[0].registration_number ?? "detected"} — investigation complete.`,
        "Investigation Complete",
      );
      return;
    }
    if (results.length > 1) {
      const successCount = results.filter((item) => item.status === "completed").length;
      if (successCount === results.length) {
        toast.success(
          `${results.length} independent investigations completed.`,
          "Investigations Complete",
        );
        return;
      }
      if (successCount > 0) {
        toast.success(
          `${successCount} of ${results.length} investigations completed. Failed rectangles are shown below.`,
          "Partial Investigations Complete",
        );
      }
    }
  }, [error, results, toast]);

  useEffect(() => {
    if (!vehicleImage) {
      setVehicleImageUrl(null);
      return;
    }
    const objectUrl = URL.createObjectURL(vehicleImage);
    setVehicleImageUrl(objectUrl);
    return () => URL.revokeObjectURL(objectUrl);
  }, [vehicleImage]);

  const clearVehicleImage = useCallback(() => {
    setVehicleImage(null);
    setWorkflowStarted(false);
    reset();
  }, [reset]);

  const handleImageSelected = useCallback(
    async (file: File) => {
      setWorkflowStarted(false);
      reset();
      setVehicleImage(file);
      setWorkflowStarted(true);
      try {
        await startSmartWorkflow(file);
      } catch {
        // surfaced via hook + toast
      }
    },
    [reset, startSmartWorkflow],
  );

  function handleMethodChange(nextMethod: VerificationMethod) {
    setMethod(nextMethod);
    clearVehicleImage();
    if (nextMethod === "camera") {
      setCameraSessionKey((value) => value + 1);
    }
  }

  async function handleVerifyRectangles() {
    if (!vehicleImage || isVerifying || regions.length === 0) return;
    try {
      await verifyRectangles(vehicleImage, regions);
    } catch {
      // surfaced via hook + toast
    }
  }

  const handleCapturedFile = useCallback(
    (file: File) => {
      void handleImageSelected(file);
    },
    [handleImageSelected],
  );

  const showAutoStatus =
    workflowStarted && workflowMode === "auto" && (isDetecting || isVerifying || results.length === 0);
  const showRectangleEditor =
    workflowStarted && workflowMode === "manual" && Boolean(vehicleImage && vehicleImageUrl);
  const regionThumbnails = useVehicleRegionThumbnails(vehicleImageUrl, regions);

  return (
    <AppLayout>
      <div className="space-y-8">
        <PageHeader
          badge="Vision AI"
          title="Vehicle Verification"
          description="Single vehicles are verified automatically. Multiple vehicles use rectangle selection for independent investigation."
        />

        <Card accent>
          <VerificationMethodSelector
            selected={method}
            onSelect={handleMethodChange}
            disabled={loading || isVerifying || isDetecting}
          />
        </Card>

        {method === "upload" && (
          <Card
            title="Upload Image"
            description="Upload a clear photo showing one or more vehicles"
            icon={<ShieldCheck className="h-4 w-4" />}
          >
            <div className="space-y-5">
              <ImageUploadZone
                disabled={loading || isVerifying || isDetecting}
                onFileSelected={(file) => {
                  void handleImageSelected(file);
                }}
                onFileCleared={clearVehicleImage}
              />
            </div>
          </Card>
        )}

        {method === "camera" && (
          <Card
            title="Live Camera"
            description="Capture a live photo — single vehicles verify automatically, multiple vehicles use rectangle selection"
            icon={<ShieldCheck className="h-4 w-4" />}
          >
            <LiveCameraCapture
              key={cameraSessionKey}
              disabled={loading || isVerifying || isDetecting}
              verifying={loading || isVerifying}
              hideCapturedVerify
              onCapturedFile={handleCapturedFile}
              onVerify={() => void handleVerifyRectangles()}
              onSwitchToUpload={() => handleMethodChange("upload")}
              onClose={() => {
                handleMethodChange("upload");
              }}
              onCancel={() => {
                setMethod(null);
                clearVehicleImage();
              }}
            />
          </Card>
        )}

        {showAutoStatus && (
          <Card
            title="Automatic Investigation"
            description="Single vehicle detected — verification runs without rectangle selection"
            icon={<ShieldCheck className="h-4 w-4" />}
          >
            <SmartVerificationStatus
              detecting={isDetecting}
              verifying={isVerifying}
              detectedCount={detectedCount}
            />
          </Card>
        )}

        {showRectangleEditor && vehicleImageUrl && (
          <Card
            title="Vehicle Rectangles"
            description="Create, move, resize, or delete rectangles — one per vehicle"
            icon={<ShieldCheck className="h-4 w-4" />}
          >
            {detectionError && (
              <div className="mb-4">
                <Alert variant="warning" title="Detection Notice">
                  {detectionError}
                </Alert>
              </div>
            )}
            <MultiRectangleSelector
              imageUrl={vehicleImageUrl}
              regions={regions}
              selectedRegionId={selectedRegionId}
              detectedCount={detectedCount}
              disabled={loading || isVerifying}
              verifying={isVerifying}
              onRegionsChange={setRegions}
              onSelectedRegionChange={setSelectedRegionId}
              onVerify={() => void handleVerifyRectangles()}
            />
          </Card>
        )}

        {(loading || isDetecting) && (
          <AiProcessingProgress
            active
            title={
              isDetecting
                ? "Detecting Vehicles"
                : workflowMode === "auto"
                  ? "Starting Automatic Investigation"
                  : "Running Vision AI Investigation"
            }
            statusMessage={loadingMessage}
          />
        )}

        {error && !loading && !isDetecting && results.length === 0 && (
          <Alert variant="error" title="Verification Failed">
            {error}
          </Alert>
        )}

        {results.length > 0 && !loading && !isDetecting && (
          <VehicleInvestigationResults
            results={results}
            vehicleImageUrl={vehicleImageUrl}
            regions={regions}
            thumbnails={regionThumbnails}
          />
        )}
      </div>
    </AppLayout>
  );
}
