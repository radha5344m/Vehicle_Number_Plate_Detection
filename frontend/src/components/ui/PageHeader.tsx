import type { ReactNode } from "react";

import { BackButton } from "@/components/ui/BackButton";

interface PageHeaderProps {
  title: string;
  description?: string;
  badge?: string;
  actions?: ReactNode;
  showBack?: boolean;
}

export function PageHeader({
  title,
  description,
  badge,
  actions,
  showBack = true,
}: PageHeaderProps) {
  return (
    <div className="animate-fade-in flex flex-col gap-4 border-b border-slate-200 pb-6 lg:flex-row lg:items-end lg:justify-between">
      <div className="min-w-0 flex-1">
        {showBack ? <BackButton /> : null}
        {badge ? (
          <span className="mb-3 inline-flex items-center rounded-full bg-brand-soft px-2.5 py-1 text-xs font-semibold uppercase tracking-[0.12em] text-brand ring-1 ring-inset ring-blue-100">
            {badge}
          </span>
        ) : null}
        <h1 className="text-xl font-bold tracking-tight text-slate-900 sm:text-2xl lg:text-3xl">
          {title}
        </h1>
        {description ? (
          <p className="mt-2 max-w-2xl text-sm leading-relaxed text-slate-500">{description}</p>
        ) : null}
      </div>
      {actions ? (
        <div className="page-header-actions flex w-full shrink-0 flex-col gap-2 sm:flex-row sm:flex-wrap lg:w-auto">
          {actions}
        </div>
      ) : null}
    </div>
  );
}
