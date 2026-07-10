import { useCallback, useEffect, useRef, useState, type DragEvent } from "react";
import { ImagePlus, RefreshCw, Trash2, X } from "lucide-react";
import { formatFileSize, validateImageFile } from "@/utils/image/validateImage";
import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";

interface ImageUploadZoneProps {
  onFileSelected: (file: File) => void;
  onFileCleared?: () => void;
  disabled?: boolean;
}

export function ImageUploadZone({
  onFileSelected,
  onFileCleared,
  disabled = false,
}: ImageUploadZoneProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragActive, setDragActive] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [validationError, setValidationError] = useState<string | null>(null);

  useEffect(() => {
    return () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl);
    };
  }, [previewUrl]);

  const processFile = useCallback(
    async (file: File) => {
      setValidationError(null);
      const validation = await validateImageFile(file);
      if (!validation.valid) {
        setValidationError(validation.error ?? "Invalid image");
        return;
      }

      if (previewUrl) URL.revokeObjectURL(previewUrl);
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      onFileSelected(file);
    },
    [onFileSelected, previewUrl],
  );

  function handleDragOver(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    if (!disabled) setDragActive(true);
  }

  function handleDragLeave(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    setDragActive(false);
  }

  function handleDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    setDragActive(false);
    if (disabled) return;

    const file = event.dataTransfer.files[0];
    if (file) void processFile(file);
  }

  function handleInputChange(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (file) void processFile(file);
  }

  function clearSelection() {
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setPreviewUrl(null);
    setSelectedFile(null);
    setValidationError(null);
    if (inputRef.current) inputRef.current.value = "";
    onFileCleared?.();
  }

  function openFilePicker() {
    if (!disabled) inputRef.current?.click();
  }

  return (
    <div className="space-y-4">
      {!selectedFile && (
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={openFilePicker}
          className={`group cursor-pointer rounded-2xl border-2 border-dashed p-8 text-center transition-all duration-300 ${
            dragActive
              ? "border-brand bg-brand-soft scale-[1.01]"
              : "border-slate-300 bg-slate-50 hover:border-brand/50 hover:bg-brand-soft/50"
          } ${disabled ? "cursor-not-allowed opacity-60" : ""}`}
        >
          <input
            ref={inputRef}
            type="file"
            accept="image/jpeg,image/png,image/webp"
            className="hidden"
            disabled={disabled}
            onChange={handleInputChange}
          />
          <div className="mx-auto mb-3 flex h-14 w-14 items-center justify-center rounded-2xl bg-white text-slate-400 shadow-sm ring-1 ring-slate-200 transition group-hover:bg-brand group-hover:text-white group-hover:ring-brand">
            <ImagePlus className="h-6 w-6" aria-hidden />
          </div>
          <p className="text-sm font-semibold text-slate-800">Drag &amp; drop vehicle image here</p>
          <p className="mt-1 text-xs text-slate-500">
            or click to browse · JPG / PNG / WEBP · min 640×480 · max 10 MB
          </p>
        </div>
      )}

      {validationError && (
        <Alert variant="error" title="Invalid Image">
          {validationError}
        </Alert>
      )}

      {selectedFile && previewUrl && (
        <div className="animate-slide-up space-y-4 rounded-2xl border border-slate-200 bg-white p-4 shadow-soft">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-sm font-semibold text-slate-900">{selectedFile.name}</p>
              <p className="mt-1 text-xs text-slate-500">{formatFileSize(selectedFile.size)}</p>
            </div>
            <button
              type="button"
              onClick={clearSelection}
              className="rounded-lg p-1.5 text-slate-400 transition hover:bg-red-50 hover:text-red-500"
              aria-label="Remove image"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
          <img
            src={previewUrl}
            alt="Vehicle preview"
            className="max-h-80 w-full rounded-xl bg-slate-50 object-contain ring-1 ring-slate-200"
          />
          <div className="flex flex-wrap gap-3">
            <Button
              type="button"
              variant="secondary"
              size="lg"
              icon={<RefreshCw className="h-4 w-4" />}
              disabled={disabled}
              onClick={openFilePicker}
              className="min-h-12"
            >
              Replace Image
            </Button>
            <Button
              type="button"
              variant="ghost"
              size="lg"
              icon={<Trash2 className="h-4 w-4" />}
              disabled={disabled}
              onClick={clearSelection}
              className="min-h-12"
            >
              Remove Image
            </Button>
          </div>
          <input
            ref={inputRef}
            type="file"
            accept="image/jpeg,image/png,image/webp"
            className="hidden"
            disabled={disabled}
            onChange={handleInputChange}
          />
        </div>
      )}
    </div>
  );
}
