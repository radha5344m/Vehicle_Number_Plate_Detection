import { describe, expect, it } from "vitest";

import {
  buildInvestigationFiltersFromDraft,
  investigationFiltersToDraft,
  validateInvestigationDateRange,
} from "@/lib/investigationReportFilters";

describe("investigationReportFilters", () => {
  it("rejects an inverted date range", () => {
    expect(validateInvestigationDateRange("2026-07-10", "2026-07-01")).toBe(
      "From Date must be on or before To Date.",
    );
  });

  it("builds API filters from draft values", () => {
    const filters = buildInvestigationFiltersFromDraft(
      {
        search: "AP09",
        from: "2026-07-01",
        to: "2026-07-09",
        officer: "",
        police_station: "Guntur",
        district: "",
        owner_name: "",
        risk_level: "high",
        vehicle_type: "",
        vehicle_brand: "",
        registration_number: "",
        investigation_status: "",
        verification_status: "",
        ai_confidence_min: "80",
        ai_confidence_max: "",
      },
      { page_size: 20, sort_by: "scanned_at", sort_desc: true },
    );

    expect(filters.search).toBe("AP09");
    expect(filters.police_station).toBe("Guntur");
    expect(filters.risk_level).toBe("high");
    expect(filters.ai_confidence_min).toBe(0.8);
    expect(filters.page).toBe(1);
  });

  it("round-trips filters through draft state", () => {
    const original = {
      page: 1,
      page_size: 20,
      sort_by: "scanned_at" as const,
      sort_desc: true,
      search: "test",
      risk_level: "medium" as const,
    };
    const draft = investigationFiltersToDraft(original);
    const rebuilt = buildInvestigationFiltersFromDraft(draft, original);

    expect(rebuilt.search).toBe("test");
    expect(rebuilt.risk_level).toBe("medium");
    expect(rebuilt.page).toBe(1);
  });
});
