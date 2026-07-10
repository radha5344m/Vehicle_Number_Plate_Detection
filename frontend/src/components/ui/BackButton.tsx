import { ArrowLeft } from "lucide-react";

import { useBackNavigation } from "@/hooks/navigation/useBackNavigation";

interface BackButtonProps {
  className?: string;
  label?: string;
}

export function BackButton({ className = "", label = "Back" }: BackButtonProps) {
  const goBack = useBackNavigation();

  return (
    <button
      type="button"
      onClick={goBack}
      className={`mb-3 inline-flex min-h-11 items-center gap-2 rounded-lg px-2 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-100 hover:text-slate-900 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand/30 focus-visible:ring-offset-2 ${className}`}
      aria-label={label}
    >
      <ArrowLeft className="h-4 w-4 shrink-0" aria-hidden />
      <span>{label}</span>
    </button>
  );
}
