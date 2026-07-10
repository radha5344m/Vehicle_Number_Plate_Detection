const CAPTURE_MIME = "image/jpeg";
const CAPTURE_QUALITY = 0.92;

export function captureVideoFrameToCanvas(video: HTMLVideoElement): HTMLCanvasElement {
  if (!video.videoWidth || !video.videoHeight) {
    throw new Error("Camera preview is not ready. Wait for the live feed and try again.");
  }

  const canvas = document.createElement("canvas");
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;

  const context = canvas.getContext("2d");
  if (!context) {
    throw new Error("Unable to capture image from camera.");
  }

  context.drawImage(video, 0, 0, canvas.width, canvas.height);
  return canvas;
}

export function canvasToJpegFile(
  canvas: HTMLCanvasElement,
  filename = `vehicle-capture-${Date.now()}.jpg`,
): Promise<File> {
  return new Promise((resolve, reject) => {
    canvas.toBlob(
      (blob) => {
        if (!blob) {
          reject(new Error("Capture failed. Please retake the photo and try again."));
          return;
        }
        resolve(new File([blob], filename, { type: CAPTURE_MIME, lastModified: Date.now() }));
      },
      CAPTURE_MIME,
      CAPTURE_QUALITY,
    );
  });
}

export async function captureVideoFrameToFile(
  video: HTMLVideoElement,
  filename?: string,
): Promise<File> {
  const canvas = captureVideoFrameToCanvas(video);
  return canvasToJpegFile(canvas, filename);
}

export function mapCameraError(error: unknown): { code: string; message: string } {
  if (error instanceof DOMException) {
    if (error.name === "NotAllowedError" || error.name === "PermissionDeniedError") {
      return {
        code: "permission_denied",
        message:
          "Camera permission denied. Please enable camera access in your browser settings or upload an image instead.",
      };
    }
    if (error.name === "NotFoundError" || error.name === "DevicesNotFoundError") {
      return {
        code: "not_found",
        message: "No camera detected on this device. Please upload an image instead.",
      };
    }
    if (error.name === "NotReadableError" || error.name === "TrackStartError") {
      return {
        code: "unavailable",
        message: "Camera is unavailable. It may be in use by another application.",
      };
    }
  }

  if (error instanceof Error) {
    return { code: "unknown", message: error.message };
  }

  return { code: "unknown", message: "Unable to access the camera. Please try again or upload an image." };
}
