import { Camera, ImageUp } from "lucide-react";

export type VerificationMethod = "upload" | "camera";

interface Props {
  selected: VerificationMethod | null;
  onSelect: (method: VerificationMethod) => void;
  disabled?: boolean;
}

const methods: Array<{
  key: VerificationMethod;
  label: string;
  description: string;
  icon: typeof ImageUp;
}> = [
  {
    key: "upload",
    label: "Upload Image",
    description: "Choose a photo from your device (JPG, PNG, WEBP up to 10 MB).",
    icon: ImageUp,
  },
  {
    key: "camera",
    label: "Live Camera",
    description: "Capture a live photo using your device camera or webcam.",
    icon: Camera,
  },
];

export function VerificationMethodSelector({ selected, onSelect, disabled = false }: Props) {
  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold text-slate-900">Choose Verification Method</h2>
        <p className="mt-1 text-sm text-slate-500">
          Both methods use the same Vision AI verification workflow and generate the same investigation
          report.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        {methods.map((method) => {
          const Icon = method.icon;
          const isSelected = selected === method.key;
          return (
            <button
              key={method.key}
              type="button"
              disabled={disabled}
              onClick={() => onSelect(method.key)}
              className={`rounded-2xl border p-5 text-left transition-all duration-200 ${
                isSelected
                  ? "border-brand bg-brand-soft shadow-soft ring-2 ring-brand/20"
                  : "border-slate-200 bg-white hover:border-brand/40 hover:bg-slate-50"
              } ${disabled ? "cursor-not-allowed opacity-60" : ""}`}
            >
              <div className="flex items-start gap-4">
                <div
                  className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-xl ${
                    isSelected ? "bg-brand text-white" : "bg-slate-100 text-slate-600"
                  }`}
                >
                  <Icon className="h-6 w-6" aria-hidden />
                </div>
                <div>
                  <p className="text-base font-semibold text-slate-900">{method.label}</p>
                  <p className="mt-1 text-sm text-slate-500">{method.description}</p>
                </div>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
