export interface LiveCameraCaptureMetrics {
  originalWidth: number;
  originalHeight: number;
  originalBytesSize: number | null;
  finalWidth: number;
  finalHeight: number;
  finalBytesSize: number;
}

type ImageCaptureLike = {
  takePhoto: () => Promise<Blob>;
};

function logLiveCameraCaptureMetrics(metrics: LiveCameraCaptureMetrics): void {
  console.info("[live-camera] capture metrics", metrics);
  if (
    metrics.originalWidth !== metrics.finalWidth ||
    metrics.originalHeight !== metrics.finalHeight
  ) {
    console.warn(
      "[live-camera] capture dimensions changed",
      `original=${metrics.originalWidth}x${metrics.originalHeight}`,
      `final=${metrics.finalWidth}x${metrics.finalHeight}`,
    );
  }
}

async function readImageDimensions(blob: Blob): Promise<{ width: number; height: number }> {
  const url = URL.createObjectURL(blob);
  try {
    return await new Promise((resolve, reject) => {
      const image = new Image();
      image.onload = () => {
        resolve({ width: image.naturalWidth, height: image.naturalHeight });
      };
      image.onerror = () => reject(new Error("Unable to read captured image dimensions."));
      image.src = url;
    });
  } finally {
    URL.revokeObjectURL(url);
  }
}

function createImageCapture(track: MediaStreamTrack): ImageCaptureLike | null {
  const ImageCaptureCtor = (
    globalThis as typeof globalThis & {
      ImageCapture?: new (track: MediaStreamTrack) => ImageCaptureLike;
    }
  ).ImageCapture;
  if (!ImageCaptureCtor) {
    return null;
  }
  try {
    return new ImageCaptureCtor(track);
  } catch {
    return null;
  }
}

async function captureWithImageCapture(
  video: HTMLVideoElement,
  stream: MediaStream,
  filename: string,
): Promise<{ file: File; metrics: LiveCameraCaptureMetrics }> {
  const track = stream.getVideoTracks()[0];
  if (!track) {
    throw new Error("Camera stream is not available. Please restart the camera and try again.");
  }

  const imageCapture = createImageCapture(track);
  if (!imageCapture) {
    throw new Error("ImageCapture API is unavailable.");
  }

  const originalWidth = video.videoWidth;
  const originalHeight = video.videoHeight;
  const blob = await imageCapture.takePhoto();
  const { width: finalWidth, height: finalHeight } = await readImageDimensions(blob);
  const mimeType = blob.type || "image/jpeg";
  const file = new File([blob], filename, { type: mimeType, lastModified: Date.now() });

  const metrics: LiveCameraCaptureMetrics = {
    originalWidth,
    originalHeight,
    originalBytesSize: null,
    finalWidth,
    finalHeight,
    finalBytesSize: file.size,
  };
  logLiveCameraCaptureMetrics(metrics);
  return { file, metrics };
}

async function captureWithNativeCanvas(
  video: HTMLVideoElement,
  filename: string,
): Promise<{ file: File; metrics: LiveCameraCaptureMetrics }> {
  if (!video.videoWidth || !video.videoHeight) {
    throw new Error("Camera preview is not ready. Wait for the live feed and try again.");
  }

  const originalWidth = video.videoWidth;
  const originalHeight = video.videoHeight;

  const canvas = document.createElement("canvas");
  canvas.width = originalWidth;
  canvas.height = originalHeight;

  const context = canvas.getContext("2d");
  if (!context) {
    throw new Error("Unable to capture image from camera.");
  }

  context.drawImage(video, 0, 0, originalWidth, originalHeight);

  const blob = await new Promise<Blob>((resolve, reject) => {
    canvas.toBlob(
      (result) => {
        if (!result) {
          reject(new Error("Capture failed. Please retake the photo and try again."));
          return;
        }
        resolve(result);
      },
      "image/jpeg",
      1,
    );
  });

  const file = new File([blob], filename, { type: blob.type || "image/jpeg", lastModified: Date.now() });
  const metrics: LiveCameraCaptureMetrics = {
    originalWidth,
    originalHeight,
    originalBytesSize: null,
    finalWidth: originalWidth,
    finalHeight: originalHeight,
    finalBytesSize: file.size,
  };
  logLiveCameraCaptureMetrics(metrics);
  return { file, metrics };
}

/**
 * Capture the live camera frame without resizing, cropping, or quality reduction.
 * Uses the native ImageCapture API when available; otherwise encodes the frame at
 * the exact preview resolution with maximum JPEG quality.
 */
export async function captureLiveCameraFrameToFile(
  video: HTMLVideoElement,
  stream: MediaStream | null,
  filename = `vehicle-capture-${Date.now()}.jpg`,
): Promise<File> {
  if (!video.videoWidth || !video.videoHeight) {
    throw new Error("Camera preview is not ready. Wait for the live feed and try again.");
  }

  if (stream) {
    try {
      const { file } = await captureWithImageCapture(video, stream, filename);
      return file;
    } catch (error) {
      if (error instanceof Error && error.message === "ImageCapture API is unavailable.") {
        // Fall back to a 1:1 canvas encode at native preview resolution.
      } else {
        throw error;
      }
    }
  }

  const { file } = await captureWithNativeCanvas(video, filename);
  return file;
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
