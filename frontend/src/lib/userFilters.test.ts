import { describe, expect, it } from "vitest";

import {
  buildUserFiltersFromDraft,
  getUserFiltersValidationError,
  sanitizeUserFilters,
  validateDateRange,
} from "@/lib/userFilters";

describe("userFilters", () => {
  it("rejects an inverted created-date range", () => {
    expect(validateDateRange("2026-07-10", "2026-07-01")).toBe(
      "Created From must be on or before Created To.",
    );
  });

  it("sanitizes invalid created-date ranges before requests", () => {
    const sanitized = sanitizeUserFilters({
      page: 1,
      page_size: 20,
      created_from: "2026-07-10T00:00:00.000Z",
      created_to: "2026-07-01T00:00:00.000Z",
    });

    expect(sanitized.created_from).toBeUndefined();
    expect(sanitized.created_to).toBeUndefined();
  });

  it("builds API filters from draft values", () => {
    const filters = buildUserFiltersFromDraft(
      {
        search: "admin",
        role: "STATION_ADMIN",
        station: "",
        status: "active",
        created_from: "2026-07-01",
        created_to: "2026-07-09",
      },
      { page_size: 20, sort_by: "created_at", sort_desc: true },
    );

    expect(filters.search).toBe("admin");
    expect(filters.role).toBe("STATION_ADMIN");
    expect(filters.status).toBe("active");
    expect(filters.created_from).toBeTruthy();
    expect(filters.created_to).toBeTruthy();
    expect(getUserFiltersValidationError(filters)).toBeNull();
  });
});
