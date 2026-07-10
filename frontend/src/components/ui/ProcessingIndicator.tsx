import { useEffect, useState } from "react";
import { ProgressBar } from "@/components/ui/ProgressBar";
import { Spinner } from "@/components/ui/Spinner";

interface ProcessingIndicatorProps {
  active: boolean;
  label?: string;
}

export function ProcessingIndicator({
  active,
  label = "AI processing…",
}: ProcessingIndicatorProps) {
  const [value, setValue] = useState(12);

  useEffect(() => {
    if (!active) {
      setValue(12);
      return;
    }

    const interval = window.setInterval(() => {
      setValue((current) => (current >= 92 ? 18 : current + 7));
    }, 450);

    return () => window.clearInterval(interval);
  }, [active]);

  if (!active) return null;

  return (
    <div className="animate-fade-in space-y-3 rounded-2xl border border-teal-200 bg-teal-50/60 p-5 shadow-soft ring-1 ring-teal-100">
      <Spinner label={label} />
      <ProgressBar value={value} animated showPercent={false} />
    </div>
  );
}
