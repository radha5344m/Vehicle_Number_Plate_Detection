import { describe, expect, it } from "vitest";

import { mapCameraError } from "@/utils/image/captureFrame";

describe("captureFrame", () => {
  it("maps permission denied errors", () => {
    const mapped = mapCameraError(new DOMException("denied", "NotAllowedError"));
    expect(mapped.code).toBe("permission_denied");
    expect(mapped.message).toContain("Camera permission denied");
  });

  it("maps missing camera errors", () => {
    const mapped = mapCameraError(new DOMException("missing", "NotFoundError"));
    expect(mapped.code).toBe("not_found");
    expect(mapped.message).toContain("No camera detected");
  });

  it("maps generic errors", () => {
    const mapped = mapCameraError(new Error("Capture failed"));
    expect(mapped.code).toBe("unknown");
    expect(mapped.message).toBe("Capture failed");
  });
});
