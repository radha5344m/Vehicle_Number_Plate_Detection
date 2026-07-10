import type { ReactNode } from "react";

interface ChartCardProps {
  title: string;
  description?: string;
  children: ReactNode;
}

export function ChartCard({ title, description, children }: ChartCardProps) {
  return (
    <section className="animate-fade-in rounded-2xl border border-slate-200 bg-white p-4 shadow-soft transition-all duration-300 hover:shadow-soft-lg sm:p-6">
      <div className="mb-4 border-b border-slate-100 pb-3">
        <h2 className="text-sm font-semibold text-slate-900">{title}</h2>
        {description && (
          <p className="mt-1 text-xs leading-relaxed text-slate-500">{description}</p>
        )}
      </div>
      <div className="table-scroll h-56 min-w-0 overflow-x-auto sm:h-64">{children}</div>
    </section>
  );
}
