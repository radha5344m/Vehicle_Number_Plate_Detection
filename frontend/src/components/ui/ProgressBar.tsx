interface ProgressBarProps {
  value: number;
  max?: number;
  label?: string;
  showPercent?: boolean;
  animated?: boolean;
  className?: string;
}

export function ProgressBar({
  value,
  max = 100,
  label,
  showPercent = true,
  animated = false,
  className = "",
}: ProgressBarProps) {
  const percent = Math.min(100, Math.max(0, (value / max) * 100));

  return (
    <div className={`space-y-1.5 ${className}`}>
      {(label || showPercent) && (
        <div className="flex items-center justify-between text-xs">
          {label && <span className="font-medium text-slate-500">{label}</span>}
          {showPercent && (
            <span className="font-mono font-semibold text-brand">{Math.round(percent)}%</span>
          )}
        </div>
      )}
      <div
        className="relative h-2.5 overflow-hidden rounded-full bg-slate-100 ring-1 ring-inset ring-slate-200"
        role="progressbar"
        aria-valuenow={percent}
        aria-valuemin={0}
        aria-valuemax={100}
      >
        <div
          className={`relative h-full rounded-full bg-gradient-to-r from-brand to-secondary transition-all duration-500 ease-out ${animated ? "progress-shimmer" : ""}`}
          style={{ width: `${percent}%` }}
        />
      </div>
    </div>
  );
}
