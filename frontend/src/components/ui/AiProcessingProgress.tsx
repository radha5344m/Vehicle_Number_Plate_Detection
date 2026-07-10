import { useEffect, useState } from "react";
import {
  Brain,
  Check,
  FileText,
  Save,
  Shield,
  Upload,
  UserSearch,
} from "lucide-react";
import { ProgressBar } from "@/components/ui/ProgressBar";
import { WORKFLOW_STAGE_LABELS } from "@/types/api/workflow";

const WORKFLOW_STAGES = [
  { id: "upload", icon: Upload },
  { id: "vision_analysis", icon: Brain },
  { id: "registry_verification", icon: UserSearch },
  { id: "risk_assessment", icon: Shield },
  { id: "save_investigation", icon: Save },
  { id: "report_generation", icon: FileText },
] as const;

interface AiProcessingProgressProps {
  active?: boolean;
  title?: string;
}

export function AiProcessingProgress({
  active = true,
  title = "Vision AI Investigation in Progress",
}: AiProcessingProgressProps) {
  const [stageIndex, setStageIndex] = useState(0);

  useEffect(() => {
    if (!active) {
      setStageIndex(0);
      return;
    }

    const interval = window.setInterval(() => {
      setStageIndex((current) => Math.min(current + 1, WORKFLOW_STAGES.length - 1));
    }, 1800);

    return () => window.clearInterval(interval);
  }, [active]);

  if (!active) return null;

  const currentStage = WORKFLOW_STAGES[stageIndex];
  const StageIcon = currentStage.icon;
  const overallPercent = Math.round(((stageIndex + 1) / WORKFLOW_STAGES.length) * 100);
  const currentLabel = WORKFLOW_STAGE_LABELS[currentStage.id] ?? currentStage.id;

  return (
    <div className="animate-fade-in rounded-2xl border border-blue-200 bg-gradient-to-br from-white to-blue-50/40 p-6 shadow-soft ring-1 ring-blue-100">
      <div className="mb-5 flex items-center gap-3">
        <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-brand text-white shadow-md shadow-blue-600/25 animate-pulse-glow">
          <StageIcon className="h-5 w-5" aria-hidden />
        </div>
        <div>
          <p className="text-sm font-semibold text-slate-900">{title}</p>
          <p className="text-xs font-medium text-brand transition-all duration-300">
            {currentLabel}…
          </p>
        </div>
      </div>

      <ProgressBar value={overallPercent} label="Investigation progress" animated />

      <ol className="relative mt-6 space-y-0 border-l-2 border-blue-100 pl-4" aria-label="Vision AI workflow stages">
        {WORKFLOW_STAGES.map((stage, index) => {
          const Icon = stage.icon;
          const isComplete = index < stageIndex;
          const isCurrent = index === stageIndex;
          const label = WORKFLOW_STAGE_LABELS[stage.id] ?? stage.id;

          return (
            <li key={stage.id} className="relative pb-4 last:pb-0">
              <span
                className={`absolute -left-[1.3rem] top-0.5 flex h-5 w-5 items-center justify-center rounded-full border-2 ${
                  isComplete
                    ? "border-green-500 bg-green-500 text-white"
                    : isCurrent
                      ? "border-brand bg-white text-brand"
                      : "border-slate-200 bg-white text-slate-300"
                }`}
              >
                {isComplete ? (
                  <Check className="h-3 w-3" aria-hidden />
                ) : (
                  <Icon className="h-2.5 w-2.5" aria-hidden />
                )}
              </span>
              <p
                className={`text-sm font-medium ${
                  isCurrent ? "text-brand" : isComplete ? "text-green-700" : "text-slate-400"
                }`}
              >
                {label}
              </p>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
