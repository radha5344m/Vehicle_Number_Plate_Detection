import type { ReactNode } from "react";

interface CardProps {
  title?: string;
  description?: string;
  children: ReactNode;
  className?: string;
  icon?: ReactNode;
  accent?: boolean;
}

export function Card({
  title,
  description,
  children,
  className = "",
  icon,
  accent = false,
}: CardProps) {
  return (
    <div
      className={`animate-fade-in rounded-2xl border bg-white p-4 shadow-soft transition-all duration-300 hover:shadow-soft-lg sm:p-6 ${
        accent
          ? "border-blue-200 ring-1 ring-blue-100"
          : "border-slate-200"
      } ${className}`}
    >
      {(title || description) && (
        <div className="mb-5 flex items-start gap-3">
          {icon && (
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-brand-soft text-brand">
              {icon}
            </div>
          )}
          <div>
            {title && <h3 className="text-base font-semibold text-slate-900">{title}</h3>}
            {description && (
              <p className="mt-0.5 text-sm leading-relaxed text-slate-500">{description}</p>
            )}
          </div>
        </div>
      )}
      {children}
    </div>
  );
}
