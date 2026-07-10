const ALLOWED_TYPES = new Set(["image/jpeg", "image/png", "image/webp"]);
const MAX_BYTES = 10 * 1024 * 1024;
const MIN_WIDTH = 640;
const MIN_HEIGHT = 480;

export function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function validateImageFile(file: File): Promise<import("@/types/api/upload").ImageValidationResult> {
  if (!ALLOWED_TYPES.has(file.type)) {
    return Promise.resolve({
      valid: false,
      error: "Only JPG, JPEG, PNG, and WEBP images are allowed",
    });
  }

  if (file.size > MAX_BYTES) {
    return Promise.resolve({ valid: false, error: "Image must not exceed 10 MB" });
  }

  return new Promise((resolve) => {
    const url = URL.createObjectURL(file);
    const image = new Image();

    image.onload = () => {
      URL.revokeObjectURL(url);
      if (image.width < MIN_WIDTH || image.height < MIN_HEIGHT) {
        resolve({
          valid: false,
          error: `Image must be at least ${MIN_WIDTH}x${MIN_HEIGHT} pixels`,
          width: image.width,
          height: image.height,
        });
        return;
      }
      resolve({ valid: true, width: image.width, height: image.height });
    };

    image.onerror = () => {
      URL.revokeObjectURL(url);
      resolve({ valid: false, error: "Unable to read image file" });
    };

    image.src = url;
  });
}
