import { useState, type FormEvent } from "react";
import { Download, FileText } from "lucide-react";
import { useGenerateInvestigationReport } from "@/hooks/reports/useGenerateInvestigationReport";
import { AppLayout } from "@/layouts/AppLayout";
import type { RiskLevel } from "@/types/api/report";
import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { PageHeader } from "@/components/ui/PageHeader";
import { ProcessingIndicator } from "@/components/ui/ProcessingIndicator";

export function InvestigationReportPage() {
  const { generate, download, result, loading, error, reset } =
    useGenerateInvestigationReport();
  const [vehicleImage, setVehicleImage] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  function handleImageChange(file: File | null) {
    setVehicleImage(file);
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setPreviewUrl(file ? URL.createObjectURL(file) : null);
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!vehicleImage) return;
    reset();

    const form = new FormData(event.currentTarget);
    const riskLevel = String(form.get("risk_level")) as RiskLevel;

    try {
      await generate(vehicleImage, {
        detected_plate: String(form.get("detected_plate")),
        ocr_registration_number: String(form.get("ocr_registration_number")),
        ocr_detected_text: String(form.get("ocr_detected_text")),
        ocr_confidence: Number(form.get("ocr_confidence")),
        risk_score: Number(form.get("risk_score")),
        risk_level: riskLevel,
        recommendation: String(form.get("recommendation")),
        vehicle_details: {
          plate_number: String(form.get("vehicle_plate") || ""),
          make: String(form.get("vehicle_make") || ""),
          model: String(form.get("vehicle_model") || ""),
          color: String(form.get("vehicle_color") || ""),
          vehicle_type: String(form.get("vehicle_type") || ""),
          registration_status: String(form.get("registration_status") || ""),
          registered_owner: String(form.get("registered_owner") || ""),
        },
      });
    } catch {
      // surfaced via hook
    }
  }

  return (
    <AppLayout>
      <div className="mx-auto max-w-4xl space-y-6">
        <PageHeader
          badge="Reporting"
          title="Investigation Report"
          description="Generate an official police investigation PDF with case metadata, Vision AI analysis, registry verification, attribute comparison, risk analytics, timeline, and recommendations."
        />

        <form onSubmit={(event) => void handleSubmit(event)} className="space-y-6">
          <Card title="Vehicle Image" icon={<FileText className="h-4 w-4" />} accent>
            <input
              type="file"
              accept="image/jpeg,image/png,image/webp"
              required
              className="block w-full text-sm text-slate-600 file:mr-4 file:rounded-lg file:border-0 file:bg-brand file:px-4 file:py-2 file:text-sm file:font-semibold file:text-white hover:file:bg-brand-hover"
              onChange={(event) => handleImageChange(event.target.files?.[0] ?? null)}
            />
            {previewUrl && (
              <img
                src={previewUrl}
                alt="Vehicle preview"
                className="mt-4 max-h-56 rounded-xl border border-slate-200 bg-slate-50 object-contain"
              />
            )}
          </Card>

          <Card title="Vision AI Analysis">
            <div className="grid gap-4 md:grid-cols-2">
            <Input name="detected_plate" label="Registration Number" required defaultValue="AP09AB1234" className="font-mono" />
            <Input name="ocr_registration_number" label="Normalized Registration" required defaultValue="AP09AB1234" className="font-mono" />
            <Input name="ocr_detected_text" label="Raw Vision Readout" required defaultValue="AP09AB1234" className="font-mono" />
            <Input name="ocr_confidence" label="Vision Confidence" type="number" min="0" max="1" step="0.01" required defaultValue="0.92" />
            </div>
          </Card>

          <section className="grid gap-4 rounded-2xl border border-slate-200 bg-white p-6 shadow-soft md:grid-cols-2">
            <h2 className="md:col-span-2 text-sm font-semibold uppercase tracking-wide text-brand">
              Vehicle Details
            </h2>
            <label className="block text-sm">
              <span className="mb-1.5 block font-medium text-slate-700">Plate Number</span>
              <input
                name="vehicle_plate"
                defaultValue="AP09AB1234"
                className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-slate-900 shadow-sm outline-none transition-all duration-200 hover:border-slate-400 focus:border-brand focus:ring-2 focus:ring-blue-500/20"
              />
            </label>
            <label className="block text-sm">
              <span className="mb-1.5 block font-medium text-slate-700">Make</span>
              <input
                name="vehicle_make"
                defaultValue="Toyota"
                className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-slate-900 shadow-sm outline-none transition-all duration-200 hover:border-slate-400 focus:border-brand focus:ring-2 focus:ring-blue-500/20"
              />
            </label>
            <label className="block text-sm">
              <span className="mb-1.5 block font-medium text-slate-700">Model</span>
              <input
                name="vehicle_model"
                defaultValue="Innova Crysta"
                className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-slate-900 shadow-sm outline-none transition-all duration-200 hover:border-slate-400 focus:border-brand focus:ring-2 focus:ring-blue-500/20"
              />
            </label>
            <label className="block text-sm">
              <span className="mb-1.5 block font-medium text-slate-700">Color</span>
              <input
                name="vehicle_color"
                defaultValue="White"
                className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-slate-900 shadow-sm outline-none transition-all duration-200 hover:border-slate-400 focus:border-brand focus:ring-2 focus:ring-blue-500/20"
              />
            </label>
            <label className="block text-sm">
              <span className="mb-1.5 block font-medium text-slate-700">Vehicle Type</span>
              <input
                name="vehicle_type"
                defaultValue="car"
                className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-slate-900 shadow-sm outline-none transition-all duration-200 hover:border-slate-400 focus:border-brand focus:ring-2 focus:ring-blue-500/20"
              />
            </label>
            <label className="block text-sm">
              <span className="mb-1.5 block font-medium text-slate-700">Registration Status</span>
              <input
                name="registration_status"
                defaultValue="active"
                className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-slate-900 shadow-sm outline-none transition-all duration-200 hover:border-slate-400 focus:border-brand focus:ring-2 focus:ring-blue-500/20"
              />
            </label>
            <label className="block text-sm md:col-span-2">
              <span className="mb-1.5 block font-medium text-slate-700">Registered Owner</span>
              <input
                name="registered_owner"
                defaultValue="Ravi Kumar"
                className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-slate-900 shadow-sm outline-none transition-all duration-200 hover:border-slate-400 focus:border-brand focus:ring-2 focus:ring-blue-500/20"
              />
            </label>
          </section>

          <section className="grid gap-4 rounded-2xl border border-slate-200 bg-white p-6 shadow-soft md:grid-cols-2">
            <h2 className="md:col-span-2 text-sm font-semibold uppercase tracking-wide text-brand">
              Risk Assessment
            </h2>
            <label className="block text-sm">
              <span className="mb-1.5 block font-medium text-slate-700">Risk Score</span>
              <input
                name="risk_score"
                type="number"
                min="0"
                max="1"
                step="0.01"
                required
                defaultValue="0.15"
                className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-slate-900 shadow-sm outline-none transition-all duration-200 hover:border-slate-400 focus:border-brand focus:ring-2 focus:ring-blue-500/20"
              />
            </label>
            <label className="block text-sm">
              <span className="mb-1.5 block font-medium text-slate-700">Risk Level</span>
              <select
                name="risk_level"
                defaultValue="low"
                className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-slate-900 shadow-sm outline-none transition-all duration-200 hover:border-slate-400 focus:border-brand focus:ring-2 focus:ring-blue-500/20"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>
            </label>
            <label className="block text-sm md:col-span-2">
              <span className="mb-1.5 block font-medium text-slate-700">Recommendation</span>
              <textarea
                name="recommendation"
                required
                rows={3}
                defaultValue="Proceed with routine checks."
                className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-slate-900 shadow-sm outline-none transition-all duration-200 hover:border-slate-400 focus:border-brand focus:ring-2 focus:ring-blue-500/20"
              />
            </label>
          </section>

          <Button
            type="submit"
            loading={loading}
            disabled={!vehicleImage}
            icon={<FileText className="h-4 w-4" />}
          >
            Generate Investigation Report
          </Button>
        </form>

        <ProcessingIndicator active={loading} label="Generating PDF report…" />

        {error && (
          <Alert variant="error" title="Report Generation Failed">
            {error}
          </Alert>
        )}

        {result && (
          <Alert variant="success" title={result.title}>
            <p>
              Report ID: <span className="font-mono">{result.report_id}</span>
            </p>
            <p className="mt-1">
              Size: {(result.file_size_bytes / 1024).toFixed(1)} KB · Generated{" "}
              {new Date(result.generated_at).toLocaleString()}
            </p>
            <Button
              variant="secondary"
              className="mt-4"
              onClick={() => void download()}
              icon={<Download className="h-4 w-4" />}
            >
              Download PDF
            </Button>
          </Alert>
        )}
      </div>
    </AppLayout>
  );
}
