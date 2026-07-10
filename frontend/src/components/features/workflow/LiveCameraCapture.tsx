import { Camera, RefreshCw, RotateCcw, ShieldCheck, SwitchCamera, X } from "lucide-react";

import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { useLiveCamera } from "@/hooks/camera/useLiveCamera";

interface Props {
  disabled?: boolean;
  verifying?: boolean;
  onCapturedFile: (file: File) => void;
  onVerify: () => void;
  onSwitchToUpload: () => void;
  onClose: () => void;
  onCancel?: () => void;
}

export function LiveCameraCapture({
  disabled = false,
  verifying = false,
  onCapturedFile,
  onVerify,
  onSwitchToUpload,
  onClose,
  onCancel,
}: Props) {
  const camera = useLiveCamera({ autoStart: true });

  async function handleCapture() {
    const file = await camera.capture();
    if (file) {
      onCapturedFile(file);
    }
  }

  const isPermissionDenied = camera.errorCode === "permission_denied";
  const showLivePreview = camera.status === "live" || camera.status === "starting";
  const showCapturedPreview = camera.status === "captured" && camera.capturedPreviewUrl;

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="text-base font-semibold text-slate-900">Live Camera</h3>
          <p className="text-sm text-slate-500">
            Position the registration plate in frame, then capture a single photo for verification.
          </p>
        </div>
        <Button
          type="button"
          variant="ghost"
          size="sm"
          icon={<X className="h-4 w-4" />}
          onClick={() => {
            camera.stop();
            onClose();
          }}
        >
          Close Camera
        </Button>
      </div>

      {camera.errorMessage && (
        <Alert variant="error" title={isPermissionDenied ? "Camera Permission Denied" : "Camera Error"}>
          <p>{camera.errorMessage}</p>
          {isPermissionDenied && (
            <div className="mt-3">
              <Button type="button" variant="secondary" size="sm" onClick={onSwitchToUpload}>
                Upload Image
              </Button>
            </div>
          )}
        </Alert>
      )}

      {showLivePreview && (
        <div className="relative overflow-hidden rounded-2xl border border-slate-200 bg-slate-950 shadow-soft">
          <video
            ref={camera.videoRef}
            autoPlay
            playsInline
            muted
            className="aspect-[4/3] w-full object-cover"
          />
          <div className="pointer-events-none absolute inset-0 border border-white/20">
            <div className="absolute inset-6 rounded-xl border-2 border-dashed border-white/50" />
          </div>
          {camera.status === "starting" && (
            <div className="absolute inset-0 flex items-center justify-center bg-slate-950/70 text-sm font-medium text-white">
              Starting camera…
            </div>
          )}
        </div>
      )}

      {showCapturedPreview && (
        <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white p-4 shadow-soft">
          <p className="mb-3 text-sm font-medium text-slate-700">Captured Preview</p>
          <img
            src={camera.capturedPreviewUrl}
            alt="Captured vehicle"
            className="max-h-96 w-full rounded-xl bg-slate-50 object-contain ring-1 ring-slate-200"
          />
        </div>
      )}

      <div className="flex flex-col gap-3 sm:flex-row sm:flex-wrap">
        {camera.status === "live" && (
          <>
            <Button
              type="button"
              size="lg"
              icon={<Camera className="h-5 w-5" />}
              disabled={disabled || verifying || camera.status !== "live"}
              onClick={() => void handleCapture()}
              className="min-h-11 w-full sm:min-h-12 sm:w-auto sm:flex-none"
            >
              Capture
            </Button>
            <Button
              type="button"
              variant="secondary"
              size="lg"
              icon={<SwitchCamera className="h-5 w-5" />}
              disabled={disabled || verifying || !camera.canSwitchCamera}
              onClick={() => void camera.switchCamera()}
              className="min-h-11 w-full sm:min-h-12 sm:w-auto"
            >
              Switch Camera
            </Button>
          </>
        )}

        {camera.status === "captured" && (
          <>
            <Button
              type="button"
              variant="secondary"
              size="lg"
              icon={<RotateCcw className="h-5 w-5" />}
              disabled={disabled || verifying}
              onClick={camera.retake}
              className="min-h-11 w-full sm:min-h-12 sm:w-auto"
            >
              Retake
            </Button>
            <Button
              type="button"
              size="lg"
              icon={<ShieldCheck className="h-5 w-5" />}
              loading={verifying}
              disabled={disabled || verifying || !camera.capturedFile}
              onClick={onVerify}
              className="min-h-11 w-full sm:min-h-12 sm:w-auto sm:flex-none"
            >
              Verify Vehicle
            </Button>
            <Button
              type="button"
              variant="ghost"
              size="lg"
              disabled={disabled || verifying}
              onClick={() => {
                camera.stop();
                onCancel?.();
              }}
              className="min-h-11 w-full sm:min-h-12 sm:w-auto"
            >
              Cancel
            </Button>
          </>
        )}

        {(camera.status === "error" || camera.status === "idle") && !isPermissionDenied && (
          <Button
            type="button"
            variant="secondary"
            size="lg"
            icon={<RefreshCw className="h-5 w-5" />}
            disabled={disabled || verifying}
            onClick={() => void camera.start()}
            className="min-h-11 w-full sm:min-h-12 sm:w-auto"
          >
            Retry Camera
          </Button>
        )}
      </div>
    </div>
  );
}
