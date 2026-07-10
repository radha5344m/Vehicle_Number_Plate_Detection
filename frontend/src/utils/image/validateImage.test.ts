import { describe, expect, it } from "vitest";

import { validateImageFile } from "@/utils/image/validateImage";

describe("validateImageFile", () => {
  it("rejects unsupported formats", async () => {
    const file = new File([new Uint8Array([1, 2, 3])], "vehicle.gif", { type: "image/gif" });
    const result = await validateImageFile(file);
    expect(result.valid).toBe(false);
    expect(result.error).toContain("WEBP");
  });
});
