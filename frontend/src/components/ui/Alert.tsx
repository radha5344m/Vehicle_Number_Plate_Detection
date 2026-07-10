import type { ReactNode } from "react";
import { AlertCircle, AlertTriangle, CheckCircle2, Info } from "lucide-react";

type AlertVariant = "success" | "error" | "warning" | "info";

interface AlertProps {
  variant?: AlertVariant;
  title?: string;
  children: ReactNode;
  className?: string;
}

const config: Record<
  AlertVariant,
  { icon: typeof CheckCircle2; border: string; bg: string; icon_color: string; text: string; title: string }
> = {
  success: {
    icon: CheckCircle2,
    border: "border-green-200",
    bg: "bg-green-50",
    icon_color: "text-green-500",
    text: "text-green-800",
    title: "text-green-900",
  },
  error: {
    icon: AlertCircle,
    border: "border-red-200",
    bg: "bg-red-50",
    icon_color: "text-red-500",
    text: "text-red-800",
    title: "text-red-900",
  },
  warning: {
    icon: AlertTriangle,
    border: "border-amber-200",
    bg: "bg-amber-50",
    icon_color: "text-amber-500",
    text: "text-amber-800",
    title: "text-amber-900",
  },
  info: {
    icon: Info,
    border: "border-blue-200",
    bg: "bg-blue-50",
    icon_color: "text-brand",
    text: "text-blue-800",
    title: "text-blue-900",
  },
};

export function Alert({
  variant = "info",
  title,
  children,
  className = "",
}: AlertProps) {
  const { icon: Icon, border, bg, icon_color, text, title: titleColor } = config[variant];

  return (
    <div
      className={`animate-slide-up flex gap-3 rounded-xl border px-4 py-3.5 ${border} ${bg} ${className}`}
      role="alert"
    >
      <Icon className={`mt-0.5 h-5 w-5 shrink-0 ${icon_color}`} aria-hidden />
      <div className="min-w-0 flex-1">
        {title && <p className={`text-sm font-semibold ${titleColor}`}>{title}</p>}
        <div className={`text-sm ${text} ${title ? "mt-1" : ""}`}>{children}</div>
      </div>
    </div>
  );
}
