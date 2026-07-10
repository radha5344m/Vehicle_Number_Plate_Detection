import { Loader2 } from "lucide-react";

interface SpinnerProps {
  size?: "sm" | "md" | "lg";
  label?: string;
  className?: string;
}

const sizeMap = {
  sm: "h-4 w-4",
  md: "h-6 w-6",
  lg: "h-10 w-10",
};

export function Spinner({ size = "md", label, className = "" }: SpinnerProps) {
  return (
    <div className={`inline-flex items-center gap-2 ${className}`} role="status" aria-live="polite">
      <Loader2 className={`animate-spin text-brand ${sizeMap[size]}`} aria-hidden />
      {label && <span className="text-sm text-slate-500">{label}</span>}
    </div>
  );
}
