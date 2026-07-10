import {
  Ban,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  Download,
  Printer,
  RotateCcw,
  Search,
  Share2,
  Trash2,
  X,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";

import { ChallanAnalyticsSection } from "@/components/features/challans/ChallanAnalyticsSection";
import {
  ChallanStatusBadge,
  formatChallanInr,
  formatViolationLabel,
} from "@/components/features/challans/ChallanStatusBadge";
import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { LoadingState } from "@/components/ui/LoadingState";
import { PageHeader } from "@/components/ui/PageHeader";
import {
  useChallanAnalytics,
  useChallansList,
  useCreateChallan,
  useVehicleChallanSearch,
  useViolationMaster,
} from "@/hooks/challans/useChallans";
import { AppLayout } from "@/layouts/AppLayout";
import { hasRole } from "@/lib/rbac";
import { challansService } from "@/services/challansService";
import type { ChallanDetail, ChallanItem, CreateChallanPayload } from "@/types/api/challans";

type TabKey = "issue" | "pending" | "history";

const EMPTY_PENDING_FILTERS = {
  station_id: "",
  officer_id: "",
  registration_number: "",
  violation_type: "",
  issued_from: "",
  issued_to: "",
};

function SummaryRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-start justify-between gap-4 border-b border-slate-100 py-2.5 last:border-b-0">
      <dt className="text-sm text-slate-500">{label}</dt>
      <dd className="max-w-[60%] text-right text-sm font-semibold text-slate-900">{value}</dd>
    </div>
  );
}

function ChallansTable({
  items,
  onDownload,
  onCancel,
  onMarkPaid,
  onDelete,
  showActions = true,
}: {
  items: ChallanItem[];
  onDownload: (item: ChallanItem) => void;
  onCancel?: (item: ChallanItem) => void;
  onMarkPaid?: (item: ChallanItem) => void;
  onDelete?: (item: ChallanItem) => void;
  showActions?: boolean;
}) {
  if (items.length === 0) {
    return (
      <div className="rounded-xl border border-dashed border-slate-200 bg-slate-50 px-4 py-10 text-center text-sm text-slate-500">
        No challans found for the selected filters.
      </div>
    );
  }

  return (
    <div className="table-scroll overflow-x-auto rounded-xl border border-slate-200">
      <table className="min-w-full divide-y divide-slate-200 text-sm">
        <thead className="bg-slate-50 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
          <tr>
            <th className="px-4 py-3">Challan Number</th>
            <th className="px-4 py-3">Date</th>
            <th className="px-4 py-3">Registration</th>
            <th className="px-4 py-3">Violation</th>
            <th className="px-4 py-3">Fine</th>
            <th className="px-4 py-3">Status</th>
            <th className="px-4 py-3">Officer</th>
            {showActions ? <th className="px-4 py-3">Actions</th> : null}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100 bg-white">
          {items.map((item) => (
            <tr key={item.id} className="hover:bg-slate-50/80">
              <td className="px-4 py-3 font-mono font-semibold text-slate-900">{item.challan_number}</td>
              <td className="px-4 py-3 text-slate-600">{new Date(item.issued_at).toLocaleString()}</td>
              <td className="px-4 py-3 font-mono text-slate-700">{item.registration_number}</td>
              <td className="px-4 py-3 text-slate-700">
                {item.violation_description ?? formatViolationLabel(item.violation_type)}
              </td>
              <td className="px-4 py-3 font-semibold text-slate-900">{formatChallanInr(item.fine_amount)}</td>
              <td className="px-4 py-3">
                <ChallanStatusBadge status={item.payment_status} />
              </td>
              <td className="px-4 py-3 text-slate-600">{item.officer_name}</td>
              {showActions ? (
                <td className="px-4 py-3">
                  <div className="flex flex-wrap gap-1">
                    <Button size="sm" variant="ghost" icon={<Download className="h-3.5 w-3.5" />} onClick={() => onDownload(item)}>
                      PDF
                    </Button>
                    {item.payment_status === "pending" && onCancel ? (
                      <Button size="sm" variant="ghost" icon={<Ban className="h-3.5 w-3.5" />} onClick={() => onCancel(item)}>
                        Cancel
                      </Button>
                    ) : null}
                    {item.payment_status === "pending" && onMarkPaid ? (
                      <Button size="sm" variant="ghost" icon={<CheckCircle2 className="h-3.5 w-3.5" />} onClick={() => onMarkPaid(item)}>
                        Paid
                      </Button>
                    ) : null}
                    {onDelete ? (
                      <Button size="sm" variant="ghost" icon={<Trash2 className="h-3.5 w-3.5" />} onClick={() => onDelete(item)}>
                        Delete
                      </Button>
                    ) : null}
                  </div>
                </td>
              ) : null}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ChallanSuccessDialog({
  challan,
  onClose,
  onDownload,
}: {
  challan: ChallanDetail;
  onClose: () => void;
  onDownload: () => void;
}) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 p-4 backdrop-blur-sm">
      <div className="w-full max-w-lg animate-slide-up rounded-2xl border border-slate-200 bg-white p-6 shadow-xl">
        <div className="mb-4 flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-green-50 text-green-600">
              <CheckCircle2 className="h-6 w-6" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-slate-900">Challan Issued Successfully</h3>
              <p className="text-sm text-slate-500">Traffic e-Challan generated and saved.</p>
            </div>
          </div>
          <button type="button" onClick={onClose} className="rounded-lg p-1 text-slate-400 hover:bg-slate-100" aria-label="Close">
            <X className="h-5 w-5" />
          </button>
        </div>

        <dl className="mb-6 space-y-2 rounded-xl bg-slate-50 p-4">
          <SummaryRow label="Challan Number" value={challan.challan_number} />
          <SummaryRow label="Registration Number" value={challan.registration_number} />
          <SummaryRow label="Fine Amount" value={formatChallanInr(challan.fine_amount)} />
          <SummaryRow label="Payment Status" value="Pending" />
        </dl>

        <div className="flex flex-wrap gap-2">
          <Button icon={<Download className="h-4 w-4" />} onClick={onDownload}>
            Download PDF
          </Button>
          <Button variant="secondary" icon={<Printer className="h-4 w-4" />} onClick={() => window.print()}>
            Print
          </Button>
          <Button
            variant="secondary"
            icon={<Share2 className="h-4 w-4" />}
            onClick={() => {
              if (navigator.share) {
                void navigator.share({
                  title: challan.challan_number,
                  text: `e-Challan ${challan.challan_number} for ${challan.registration_number}`,
                });
              }
            }}
          >
            Share
          </Button>
        </div>
      </div>
    </div>
  );
}

export function ChallansPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialTab = (searchParams.get("tab") as TabKey) || "issue";
  const initialRegistration = searchParams.get("registration") ?? "";
  const [activeTab, setActiveTab] = useState<TabKey>(initialTab);
  const [registrationInput, setRegistrationInput] = useState(initialRegistration);
  const [ownerName, setOwnerName] = useState("");
  const [violationCode, setViolationCode] = useState("");
  const [violationDescription, setViolationDescription] = useState("");
  const [fineAmount, setFineAmount] = useState("");
  const [remarks, setRemarks] = useState("");
  const [locationLabel, setLocationLabel] = useState("");
  const [gpsCoordinates, setGpsCoordinates] = useState("");
  const [issuedChallan, setIssuedChallan] = useState<ChallanDetail | null>(null);
  const [historySearch, setHistorySearch] = useState(initialRegistration);
  const [pendingFilters, setPendingFilters] = useState({ ...EMPTY_PENDING_FILTERS });

  const canDelete = hasRole("SUPER_ADMIN");
  const canManagePayments = hasRole("SUPER_ADMIN") || hasRole("STATION_ADMIN");

  const { violations, loading: violationsLoading } = useViolationMaster();
  const { result: searchResult, loading: searchLoading, error: searchError, search, reset } =
    useVehicleChallanSearch();
  const { create, loading: createLoading, error: createError } = useCreateChallan();
  const { data: analytics, loading: analyticsLoading, refresh: refreshAnalytics } = useChallanAnalytics();

  const pendingList = useChallansList({
    pending_only: true,
    page: 1,
    page_size: 20,
    station_id: pendingFilters.station_id || undefined,
    officer_id: pendingFilters.officer_id || undefined,
    registration_number: pendingFilters.registration_number || undefined,
    violation_type: pendingFilters.violation_type || undefined,
    issued_from: pendingFilters.issued_from ? new Date(pendingFilters.issued_from).toISOString() : undefined,
    issued_to: pendingFilters.issued_to ? new Date(`${pendingFilters.issued_to}T23:59:59`).toISOString() : undefined,
  });

  const historyList = useChallansList({
    search: historySearch || undefined,
    page: 1,
    page_size: 20,
  });

  const selectedViolation = useMemo(
    () => violations.find((item) => item.violation_code === violationCode),
    [violations, violationCode],
  );

  useEffect(() => {
    if (initialRegistration && activeTab === "issue") {
      void search(initialRegistration);
    }
  }, [initialRegistration, activeTab, search]);

  useEffect(() => {
    if (initialRegistration && activeTab === "history") {
      historyList.setFilters({ search: initialRegistration, page: 1, page_size: 20 });
    }
  }, [initialRegistration, activeTab]);

  useEffect(() => {
    if (selectedViolation) {
      setFineAmount(String(selectedViolation.default_fine_amount));
    }
  }, [selectedViolation]);

  useEffect(() => {
    if (searchResult?.owner_name) {
      setOwnerName(searchResult.owner_name);
    }
  }, [searchResult]);

  function switchTab(tab: TabKey) {
    setActiveTab(tab);
    const next = new URLSearchParams(searchParams);
    next.set("tab", tab);
    setSearchParams(next, { replace: true });
  }

  async function handleSearchVehicle() {
    if (!registrationInput.trim()) return;
    await search(registrationInput.trim());
  }

  async function handleIssueChallan(event: React.FormEvent) {
    event.preventDefault();
    if (!registrationInput.trim() || !violationCode || !fineAmount) return;

    const payload: CreateChallanPayload = {
      registration_number: registrationInput.trim().toUpperCase(),
      owner_name: ownerName.trim() || searchResult?.owner_name || null,
      violation_type: violationCode,
      violation_description: violationDescription.trim() || null,
      fine_amount: Number(fineAmount),
      remarks: remarks.trim() || null,
      location_label: locationLabel.trim() || null,
      gps_coordinates: gpsCoordinates.trim() || null,
    };

    const mutation = await create(payload);
    if (!mutation) return;
    setIssuedChallan(mutation.challan);
    refreshAnalytics();
    pendingList.refresh();
    historyList.refresh();
    if (registrationInput.trim()) {
      await search(registrationInput.trim());
    }
  }

  async function handleDownload(item: ChallanItem) {
    await challansService.downloadPdf(item.id, item.challan_number);
  }

  async function handleCancel(item: ChallanItem) {
    await challansService.cancelChallan(item.id);
    pendingList.refresh();
    historyList.refresh();
    refreshAnalytics();
  }

  async function handleMarkPaid(item: ChallanItem) {
    await challansService.markPaid(item.id);
    pendingList.refresh();
    historyList.refresh();
    refreshAnalytics();
  }

  async function handleDelete(item: ChallanItem) {
    await challansService.deleteChallan(item.id);
    pendingList.refresh();
    historyList.refresh();
    refreshAnalytics();
  }

  function resetPendingFilters() {
    setPendingFilters({ ...EMPTY_PENDING_FILTERS });
    pendingList.setFilters({ pending_only: true, page: 1, page_size: 20 });
  }

  function resetHistorySearch() {
    setHistorySearch("");
    historyList.setFilters({ page: 1, page_size: 20 });
  }

  const tabs: { key: TabKey; label: string }[] = [
    { key: "issue", label: "Issue Challan" },
    { key: "pending", label: "Pending Challans" },
    { key: "history", label: "Challan History" },
  ];

  return (
    <AppLayout>
      <div className="space-y-6">
        <PageHeader
          badge="Enforcement"
          title="e-Challan Management"
          description="Issue traffic challans, track pending fines, and monitor enforcement analytics across your jurisdiction."
        />

        <ChallanAnalyticsSection data={analytics} loading={analyticsLoading} />

        <div className="flex flex-wrap gap-2 border-b border-slate-200 pb-1">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              type="button"
              onClick={() => switchTab(tab.key)}
              className={`rounded-t-lg px-4 py-2.5 text-sm font-semibold transition ${
                activeTab === tab.key
                  ? "border-b-2 border-brand bg-brand-soft text-brand"
                  : "text-slate-500 hover:bg-slate-50 hover:text-slate-800"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {activeTab === "issue" && (
          <div className="space-y-6">
            <Card title="Search Vehicle" description="Lookup registration and outstanding challans before issuing a new e-Challan">
              <form
                className="flex flex-col gap-4 md:flex-row md:items-end"
                onSubmit={(event) => {
                  event.preventDefault();
                  void handleSearchVehicle();
                }}
              >
                <div className="flex-1">
                  <Input
                    label="Registration Number *"
                    value={registrationInput}
                    onChange={(event) => setRegistrationInput(event.target.value.toUpperCase())}
                    placeholder="AP09AB1234"
                    required
                  />
                </div>
                <Button type="submit" loading={searchLoading} icon={<Search className="h-4 w-4" />}>
                  Search Vehicle
                </Button>
              </form>
            </Card>

            {searchError ? (
              <Alert variant="warning" title="Search Failed">
                {searchError}
              </Alert>
            ) : null}

            {searchLoading ? <LoadingState label="Searching vehicle registry and challans…" /> : null}

            {searchResult && !searchLoading ? (
              <>
                <Card
                  title={searchResult.vehicle_found ? "Vehicle Found" : "Vehicle Not Found"}
                  description={
                    searchResult.vehicle_found
                      ? "Registry details and enforcement history"
                      : "Vehicle not in registry — officer may still issue a challan with manual entry."
                  }
                  accent={searchResult.vehicle_found}
                >
                  <dl>
                    <SummaryRow label="Registration Number" value={searchResult.registration_number} />
                    <SummaryRow label="Owner Name" value={searchResult.owner_name ?? (ownerName || "—")} />
                    <SummaryRow label="Vehicle" value={searchResult.vehicle_name ?? "—"} />
                    <SummaryRow label="Brand" value={searchResult.brand ?? "—"} />
                    <SummaryRow label="Model" value={searchResult.model ?? "—"} />
                    <SummaryRow label="Color" value={searchResult.color ?? "—"} />
                    <SummaryRow label="Vehicle Type" value={searchResult.vehicle_type ?? "—"} />
                    <SummaryRow label="RC Status" value={searchResult.rc_status ?? "—"} />
                    <SummaryRow label="Insurance Status" value={searchResult.insurance_status} />
                    <SummaryRow label="Pollution Status" value={searchResult.pollution_status} />
                    <SummaryRow label="Outstanding Fine" value={formatChallanInr(searchResult.outstanding_fine_inr)} />
                    <SummaryRow label="Pending Challans" value={String(searchResult.pending_challans_count)} />
                    <SummaryRow
                      label="Previous Violations"
                      value={
                        searchResult.previous_violations.length > 0
                          ? searchResult.previous_violations.map(formatViolationLabel).join(", ")
                          : "—"
                      }
                    />
                    <SummaryRow label="Risk Level" value={searchResult.risk_level ?? "—"} />
                  </dl>
                </Card>

                <Card title="Existing Challans" description="All challans linked to this registration number">
                  <ChallansTable
                    items={searchResult.existing_challans}
                    onDownload={(item) => void handleDownload(item)}
                    showActions={false}
                  />
                </Card>
              </>
            ) : null}

            <Card title="Create New Challan" description="Complete violation details and issue the e-Challan">
              {violationsLoading ? (
                <LoadingState label="Loading violation master…" />
              ) : (
                <form className="grid gap-4 md:grid-cols-2" onSubmit={(event) => void handleIssueChallan(event)}>
                  <div className="md:col-span-2">
                    <label className="mb-1.5 block text-sm font-medium text-slate-700">Violation Type *</label>
                    <select
                      className="w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm"
                      value={violationCode}
                      onChange={(event) => setViolationCode(event.target.value)}
                      required
                    >
                      <option value="">Select violation</option>
                      {violations.map((item) => (
                        <option key={item.violation_code} value={item.violation_code}>
                          {item.violation_name} — {formatChallanInr(item.default_fine_amount)}
                        </option>
                      ))}
                    </select>
                  </div>

                  <Input
                    label="Violation Description"
                    value={violationDescription}
                    onChange={(event) => setViolationDescription(event.target.value)}
                    placeholder="Optional details"
                  />

                  <Input
                    label="Fine Amount (INR)"
                    type="number"
                    min={0}
                    value={fineAmount}
                    onChange={(event) => setFineAmount(event.target.value)}
                    disabled={selectedViolation ? !selectedViolation.amount_editable : false}
                    required
                  />

                  {!searchResult?.vehicle_found ? (
                    <Input
                      label="Owner Name"
                      value={ownerName}
                      onChange={(event) => setOwnerName(event.target.value)}
                      placeholder="Required when vehicle not in registry"
                    />
                  ) : null}

                  <div className="md:col-span-2">
                    <label className="mb-1.5 block text-sm font-medium text-slate-700">Officer Remarks</label>
                    <textarea
                      className="min-h-24 w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm"
                      value={remarks}
                      onChange={(event) => setRemarks(event.target.value)}
                      placeholder="Observations at checkpoint"
                    />
                  </div>

                  <Input
                    label="Location"
                    value={locationLabel}
                    onChange={(event) => setLocationLabel(event.target.value)}
                    placeholder="Checkpoint / junction"
                  />

                  <Input
                    label="GPS Coordinates (Optional)"
                    value={gpsCoordinates}
                    onChange={(event) => setGpsCoordinates(event.target.value)}
                    placeholder="16.3067, 80.4365"
                  />

                  {createError ? (
                    <div className="md:col-span-2">
                      <Alert variant="warning" title="Issue Failed">
                        {createError}
                      </Alert>
                    </div>
                  ) : null}

                  <div className="md:col-span-2 flex gap-3">
                    <Button type="submit" loading={createLoading}>
                      Issue Challan
                    </Button>
                    <Button
                      type="button"
                      variant="secondary"
                      onClick={() => {
                        reset();
                        setRegistrationInput("");
                        setViolationCode("");
                        setRemarks("");
                        setLocationLabel("");
                        setGpsCoordinates("");
                      }}
                    >
                      Reset
                    </Button>
                  </div>
                </form>
              )}
            </Card>
          </div>
        )}

        {activeTab === "pending" && (
          <div className="space-y-4">
            <Card title="Filters" description="Pending challans awaiting payment">
              <div className="grid gap-4 md:grid-cols-3">
                <Input
                  label="Station ID"
                  value={pendingFilters.station_id}
                  onChange={(event) =>
                    setPendingFilters((current) => ({ ...current, station_id: event.target.value }))
                  }
                />
                <Input
                  label="Officer ID"
                  value={pendingFilters.officer_id}
                  onChange={(event) =>
                    setPendingFilters((current) => ({ ...current, officer_id: event.target.value }))
                  }
                />
                <Input
                  label="Vehicle Registration"
                  value={pendingFilters.registration_number}
                  onChange={(event) =>
                    setPendingFilters((current) => ({ ...current, registration_number: event.target.value }))
                  }
                />
                <Input
                  label="Violation Type"
                  value={pendingFilters.violation_type}
                  onChange={(event) =>
                    setPendingFilters((current) => ({ ...current, violation_type: event.target.value }))
                  }
                />
                <Input
                  label="From Date"
                  type="date"
                  value={pendingFilters.issued_from}
                  onChange={(event) =>
                    setPendingFilters((current) => ({ ...current, issued_from: event.target.value }))
                  }
                />
                <Input
                  label="To Date"
                  type="date"
                  value={pendingFilters.issued_to}
                  onChange={(event) =>
                    setPendingFilters((current) => ({ ...current, issued_to: event.target.value }))
                  }
                />
              </div>
              <div className="mt-4 flex gap-2">
                <Button
                  onClick={() =>
                    pendingList.setFilters({
                      pending_only: true,
                      page: 1,
                      page_size: 20,
                      station_id: pendingFilters.station_id || undefined,
                      officer_id: pendingFilters.officer_id || undefined,
                      registration_number: pendingFilters.registration_number || undefined,
                      violation_type: pendingFilters.violation_type || undefined,
                      issued_from: pendingFilters.issued_from
                        ? new Date(pendingFilters.issued_from).toISOString()
                        : undefined,
                      issued_to: pendingFilters.issued_to
                        ? new Date(`${pendingFilters.issued_to}T23:59:59`).toISOString()
                        : undefined,
                    })
                  }
                >
                  Apply Filters
                </Button>
                <Button type="button" variant="secondary" icon={<RotateCcw className="h-4 w-4" />} onClick={resetPendingFilters}>
                  Reset Filters
                </Button>
              </div>
            </Card>

            {pendingList.loading ? <LoadingState label="Loading pending challans…" /> : null}
            {pendingList.error ? (
              <Alert variant="warning" title="Load Failed">
                {pendingList.error}
              </Alert>
            ) : null}
            {pendingList.data ? (
              <ChallansTable
                items={pendingList.data.items}
                onDownload={(item) => void handleDownload(item)}
                onCancel={canManagePayments ? (item) => void handleCancel(item) : undefined}
                onMarkPaid={canManagePayments ? (item) => void handleMarkPaid(item) : undefined}
                onDelete={canDelete ? (item) => void handleDelete(item) : undefined}
              />
            ) : null}
          </div>
        )}

        {activeTab === "history" && (
          <div className="space-y-4">
            <Card title="Search History" description="Search by registration, challan number, owner, officer, or vehicle">
              <form
                className="flex flex-col gap-3 md:flex-row"
                onSubmit={(event) => {
                  event.preventDefault();
                  historyList.setFilters((current) => ({ ...current, search: historySearch, page: 1 }));
                }}
              >
                <Input
                  className="flex-1"
                  label="Search"
                  value={historySearch}
                  onChange={(event) => setHistorySearch(event.target.value)}
                  placeholder="Registration, challan number, owner, officer…"
                />
                <div className="flex items-end gap-2">
                  <Button type="submit" icon={<Search className="h-4 w-4" />}>
                    Search
                  </Button>
                  <Button type="button" variant="secondary" icon={<RotateCcw className="h-4 w-4" />} onClick={resetHistorySearch}>
                    Reset Filters
                  </Button>
                </div>
              </form>
            </Card>

            {historyList.loading ? <LoadingState label="Loading challan history…" /> : null}
            {historyList.error ? (
              <Alert variant="warning" title="Load Failed">
                {historyList.error}
              </Alert>
            ) : null}
            {historyList.data ? (
              <>
                <ChallansTable
                  items={historyList.data.items}
                  onDownload={(item) => void handleDownload(item)}
                  onCancel={canManagePayments ? (item) => void handleCancel(item) : undefined}
                  onMarkPaid={canManagePayments ? (item) => void handleMarkPaid(item) : undefined}
                  onDelete={canDelete ? (item) => void handleDelete(item) : undefined}
                />
                {historyList.data.pagination.total_pages > 1 ? (
                  <div className="flex items-center justify-between">
                    <p className="text-sm text-slate-500">
                      Page {historyList.data.pagination.page} of {historyList.data.pagination.total_pages}
                    </p>
                    <div className="flex gap-2">
                      <Button
                        variant="secondary"
                        size="sm"
                        icon={<ChevronLeft className="h-4 w-4" />}
                        disabled={historyList.data.pagination.page <= 1}
                        onClick={() => historyList.setPage(historyList.data!.pagination.page - 1)}
                      >
                        Previous
                      </Button>
                      <Button
                        variant="secondary"
                        size="sm"
                        icon={<ChevronRight className="h-4 w-4" />}
                        disabled={historyList.data.pagination.page >= historyList.data.pagination.total_pages}
                        onClick={() => historyList.setPage(historyList.data!.pagination.page + 1)}
                      >
                        Next
                      </Button>
                    </div>
                  </div>
                ) : null}
              </>
            ) : null}
          </div>
        )}
      </div>

      {issuedChallan ? (
        <ChallanSuccessDialog
          challan={issuedChallan}
          onClose={() => setIssuedChallan(null)}
          onDownload={() => void challansService.downloadPdf(issuedChallan.id, issuedChallan.challan_number)}
        />
      ) : null}
    </AppLayout>
  );
}
