import { useCallback, useEffect, useState } from "react";
import { ShieldCheck } from "lucide-react";

import { LiveCameraCapture } from "@/components/features/workflow/LiveCameraCapture";
import {
  VerificationMethodSelector,
  type VerificationMethod,
} from "@/components/features/workflow/VerificationMethodSelector";
import { MultiRectangleSelector } from "@/components/features/workflow/MultiRectangleSelector";
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
    verifyRectangles,
    prepareImage,
    results,
    loading,
    isVerifying,
    error,
    loadingMessage,
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
  const [editorReady, setEditorReady] = useState(false);

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
    setEditorReady(false);
    reset();
  }, [reset]);

  const loadImageForEditing = useCallback(
    (file: File) => {
      reset();
      setVehicleImage(file);
      prepareImage();
      setEditorReady(true);
    },
    [prepareImage, reset],
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
      loadImageForEditing(file);
    },
    [loadImageForEditing],
  );

  const showRectangleEditor = Boolean(vehicleImage && vehicleImageUrl && editorReady);
  const regionThumbnails = useVehicleRegionThumbnails(vehicleImageUrl, regions);

  return (
    <AppLayout>
      <div className="space-y-8">
        <PageHeader
          badge="Vision AI"
          title="Vehicle Verification"
          description="Upload or capture a scene image, draw one rectangle per vehicle, then verify each region independently."
        />

        <Card accent>
          <VerificationMethodSelector
            selected={method}
            onSelect={handleMethodChange}
            disabled={loading || isVerifying}
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
                disabled={loading || isVerifying}
                onFileSelected={(file) => {
                  loadImageForEditing(file);
                }}
                onFileCleared={clearVehicleImage}
              />
            </div>
          </Card>
        )}

        {method === "camera" && (
          <Card
            title="Live Camera"
            description="Capture a live photo, then draw rectangles around each vehicle"
            icon={<ShieldCheck className="h-4 w-4" />}
          >
            <LiveCameraCapture
              key={cameraSessionKey}
              disabled={loading || isVerifying}
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

        {showRectangleEditor && vehicleImageUrl && (
          <Card
            title="Vehicle Rectangles"
            description="Create, move, resize, or delete rectangles — one per vehicle"
            icon={<ShieldCheck className="h-4 w-4" />}
          >
            <MultiRectangleSelector
              imageUrl={vehicleImageUrl}
              regions={regions}
              selectedRegionId={selectedRegionId}
              disabled={loading || isVerifying}
              verifying={isVerifying}
              onRegionsChange={setRegions}
              onSelectedRegionChange={setSelectedRegionId}
              onVerify={() => void handleVerifyRectangles()}
            />
          </Card>
        )}

        {loading && (
          <AiProcessingProgress
            active
            title="Running Vision AI Investigation"
            statusMessage={loadingMessage}
          />
        )}

        {error && !loading && results.length === 0 && (
          <Alert variant="error" title="Verification Failed">
            {error}
          </Alert>
        )}

        {results.length > 0 && !loading && (
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
