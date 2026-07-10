import { useCallback, useEffect, useState } from "react";
import { ShieldCheck } from "lucide-react";

import { LiveCameraCapture } from "@/components/features/workflow/LiveCameraCapture";
import {
  VerificationMethodSelector,
  type VerificationMethod,
} from "@/components/features/workflow/VerificationMethodSelector";
import { VehicleInvestigationResult } from "@/components/features/workflow/VehicleInvestigationResult";
import { ImageUploadZone } from "@/components/features/upload/ImageUploadZone";
import { AiProcessingProgress } from "@/components/ui/AiProcessingProgress";
import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { PageHeader } from "@/components/ui/PageHeader";
import { useToast } from "@/components/ui/Toast";
import { useVehicleVerificationWorkflow } from "@/hooks/workflow/useVehicleVerificationWorkflow";
import { AppLayout } from "@/layouts/AppLayout";

export function VehicleVerificationWorkflowPage() {
  const { run, result, loading, error, reset } = useVehicleVerificationWorkflow();
  const toast = useToast();
  const [method, setMethod] = useState<VerificationMethod | null>(null);
  const [vehicleImage, setVehicleImage] = useState<File | null>(null);
  const [vehicleImageUrl, setVehicleImageUrl] = useState<string | null>(null);
  const [cameraSessionKey, setCameraSessionKey] = useState(0);

  useEffect(() => {
    if (error) {
      toast.error(error, "Verification Failed");
    }
  }, [error, toast]);

  useEffect(() => {
    if (result?.status === "completed") {
      toast.success(
        `Registration ${result.registration_number ?? "detected"} — investigation complete.`,
        "Investigation Complete",
      );
    }
  }, [result, toast]);

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
    reset();
  }, [reset]);

  function handleMethodChange(nextMethod: VerificationMethod) {
    setMethod(nextMethod);
    clearVehicleImage();
    if (nextMethod === "camera") {
      setCameraSessionKey((value) => value + 1);
    }
  }

  async function handleVerify() {
    if (!vehicleImage) return;
    try {
      await run(vehicleImage);
    } catch {
      // surfaced via hook + toast
    }
  }

  const handleCapturedFile = useCallback(
    (file: File) => {
      setVehicleImage(file);
      reset();
    },
    [reset],
  );

  return (
    <AppLayout>
      <div className="space-y-8">
        <PageHeader
          badge="Vision AI"
          title="Vehicle Verification"
          description="Verify a vehicle by uploading a photo or capturing one with your device camera. Both methods run the same Vision AI investigation workflow."
        />

        <Card accent>
          <VerificationMethodSelector
            selected={method}
            onSelect={handleMethodChange}
            disabled={loading}
          />
        </Card>

        {method === "upload" && (
          <Card
            title="Upload Image"
            description="Upload a clear photo showing the registration plate"
            icon={<ShieldCheck className="h-4 w-4" />}
          >
            <div className="space-y-5">
              <ImageUploadZone
                disabled={loading}
                onFileSelected={(file) => {
                  setVehicleImage(file);
                  reset();
                }}
                onFileCleared={clearVehicleImage}
              />

              <Button
                type="button"
                loading={loading}
                disabled={!vehicleImage || loading}
                icon={<ShieldCheck className="h-4 w-4" />}
                size="lg"
                className="w-full min-h-12 sm:w-auto"
                onClick={() => void handleVerify()}
              >
                Verify Vehicle
              </Button>
            </div>
          </Card>
        )}

        {method === "camera" && (
          <Card
            title="Live Camera"
            description="Capture a live photo — only the captured frame is sent for verification"
            icon={<ShieldCheck className="h-4 w-4" />}
          >
            <LiveCameraCapture
              key={cameraSessionKey}
              disabled={loading}
              verifying={loading}
              onCapturedFile={handleCapturedFile}
              onVerify={() => void handleVerify()}
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

        {loading && <AiProcessingProgress active title="Running Vision AI Investigation" />}

        {error && !loading && (
          <Alert variant="error" title="Verification Failed">
            {error}
          </Alert>
        )}

        {result && !loading && (
          <VehicleInvestigationResult result={result} vehicleImageUrl={vehicleImageUrl} />
        )}
      </div>
    </AppLayout>
  );
}
