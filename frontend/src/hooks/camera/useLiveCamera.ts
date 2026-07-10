import { useCallback, useEffect, useRef, useState } from "react";

import { captureVideoFrameToFile, mapCameraError } from "@/utils/image/captureFrame";
import { validateImageFile } from "@/utils/image/validateImage";

export type LiveCameraStatus = "idle" | "starting" | "live" | "captured" | "error";

export type CameraFacingMode = "user" | "environment";

interface UseLiveCameraOptions {
  autoStart?: boolean;
}

interface UseLiveCameraResult {
  videoRef: React.RefObject<HTMLVideoElement | null>;
  status: LiveCameraStatus;
  facingMode: CameraFacingMode;
  capturedPreviewUrl: string | null;
  capturedFile: File | null;
  errorCode: string | null;
  errorMessage: string | null;
  canSwitchCamera: boolean;
  start: () => Promise<void>;
  stop: () => void;
  switchCamera: () => Promise<void>;
  capture: () => Promise<File | null>;
  retake: () => void;
}

function stopStream(stream: MediaStream | null) {
  stream?.getTracks().forEach((track) => track.stop());
}

export function useLiveCamera(options: UseLiveCameraOptions = {}): UseLiveCameraResult {
  const { autoStart = true } = options;
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const previewUrlRef = useRef<string | null>(null);

  const [status, setStatus] = useState<LiveCameraStatus>("idle");
  const [facingMode, setFacingMode] = useState<CameraFacingMode>("environment");
  const [deviceIds, setDeviceIds] = useState<string[]>([]);
  const [activeDeviceIndex, setActiveDeviceIndex] = useState(0);
  const [capturedPreviewUrl, setCapturedPreviewUrl] = useState<string | null>(null);
  const [capturedFile, setCapturedFile] = useState<File | null>(null);
  const [errorCode, setErrorCode] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const canSwitchCamera = deviceIds.length > 1 || status === "live" || status === "captured";

  const clearCapturedPreview = useCallback(() => {
    if (previewUrlRef.current) {
      URL.revokeObjectURL(previewUrlRef.current);
      previewUrlRef.current = null;
    }
    setCapturedPreviewUrl(null);
    setCapturedFile(null);
  }, []);

  const attachStream = useCallback((stream: MediaStream) => {
    const video = videoRef.current;
    if (!video) return;
    video.srcObject = stream;
    void video.play().catch(() => {
      // Playback can fail silently during rapid remounts; the next frame usually succeeds.
    });
  }, []);

  const refreshDevices = useCallback(async () => {
    if (!navigator.mediaDevices?.enumerateDevices) return;
    const devices = await navigator.mediaDevices.enumerateDevices();
    const videoInputs = devices.filter((device) => device.kind === "videoinput");
    setDeviceIds(videoInputs.map((device) => device.deviceId).filter(Boolean));
  }, []);

  const startWithConstraints = useCallback(
    async (nextFacingMode: CameraFacingMode, deviceId?: string) => {
      if (!navigator.mediaDevices?.getUserMedia) {
        setStatus("error");
        setErrorCode("unavailable");
        setErrorMessage("Camera is not supported in this browser. Please upload an image instead.");
        return;
      }

      setStatus("starting");
      setErrorCode(null);
      setErrorMessage(null);
      clearCapturedPreview();
      stopStream(streamRef.current);
      streamRef.current = null;

      try {
        const constraints: MediaStreamConstraints = {
          audio: false,
          video: deviceId
            ? {
                deviceId: { exact: deviceId },
                width: { ideal: 1280 },
                height: { ideal: 720 },
              }
            : {
                facingMode: { ideal: nextFacingMode },
                width: { ideal: 1280 },
                height: { ideal: 720 },
              },
        };

        const stream = await navigator.mediaDevices.getUserMedia(constraints);
        streamRef.current = stream;
        attachStream(stream);
        await refreshDevices();
        setFacingMode(nextFacingMode);
        setStatus("live");
      } catch (error) {
        const mapped = mapCameraError(error);
        setStatus("error");
        setErrorCode(mapped.code);
        setErrorMessage(mapped.message);
        stopStream(streamRef.current);
        streamRef.current = null;
      }
    },
    [attachStream, clearCapturedPreview, refreshDevices],
  );

  const start = useCallback(async () => {
    await startWithConstraints("environment");
    setActiveDeviceIndex(0);
  }, [startWithConstraints]);

  const stop = useCallback(() => {
    stopStream(streamRef.current);
    streamRef.current = null;
    const video = videoRef.current;
    if (video) {
      video.srcObject = null;
    }
    clearCapturedPreview();
    setStatus("idle");
    setErrorCode(null);
    setErrorMessage(null);
  }, [clearCapturedPreview]);

  const switchCamera = useCallback(async () => {
    if (deviceIds.length > 1) {
      const nextIndex = (activeDeviceIndex + 1) % deviceIds.length;
      setActiveDeviceIndex(nextIndex);
      await startWithConstraints(facingMode, deviceIds[nextIndex]);
      return;
    }

    const nextFacingMode: CameraFacingMode = facingMode === "environment" ? "user" : "environment";
    setActiveDeviceIndex(0);
    await startWithConstraints(nextFacingMode);
  }, [activeDeviceIndex, deviceIds, facingMode, startWithConstraints]);

  const capture = useCallback(async () => {
    const video = videoRef.current;
    if (!video || status !== "live") {
      setErrorCode("capture_failed");
      setErrorMessage("Capture failed. Ensure the live preview is active and try again.");
      return null;
    }

    try {
      const file = await captureVideoFrameToFile(video);
      const validation = await validateImageFile(file);
      if (!validation.valid) {
        setErrorCode("capture_failed");
        setErrorMessage(validation.error ?? "Captured image did not meet quality requirements.");
        return null;
      }

      clearCapturedPreview();
      const previewUrl = URL.createObjectURL(file);
      previewUrlRef.current = previewUrl;
      setCapturedPreviewUrl(previewUrl);
      setCapturedFile(file);
      stopStream(streamRef.current);
      streamRef.current = null;
      video.srcObject = null;
      setStatus("captured");
      setErrorCode(null);
      setErrorMessage(null);
      return file;
    } catch (error) {
      const mapped = mapCameraError(error);
      setErrorCode(mapped.code === "unknown" ? "capture_failed" : mapped.code);
      setErrorMessage(mapped.message);
      return null;
    }
  }, [clearCapturedPreview, status]);

  const retake = useCallback(() => {
    clearCapturedPreview();
    void startWithConstraints(facingMode, deviceIds[activeDeviceIndex]);
  }, [activeDeviceIndex, clearCapturedPreview, deviceIds, facingMode, startWithConstraints]);

  useEffect(() => {
    if (!autoStart) return;

    let active = true;
    void (async () => {
      await startWithConstraints("environment");
      if (!active) {
        stopStream(streamRef.current);
        streamRef.current = null;
      }
    })();

    return () => {
      active = false;
      stopStream(streamRef.current);
      streamRef.current = null;
      if (previewUrlRef.current) {
        URL.revokeObjectURL(previewUrlRef.current);
        previewUrlRef.current = null;
      }
    };
    // Mount/unmount only — avoid restarting the stream when callback identities change.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [autoStart]);

  return {
    videoRef,
    status,
    facingMode,
    capturedPreviewUrl,
    capturedFile,
    errorCode,
    errorMessage,
    canSwitchCamera,
    start,
    stop,
    switchCamera,
    capture,
    retake,
  };
}
