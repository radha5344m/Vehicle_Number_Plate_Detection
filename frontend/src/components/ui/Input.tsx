import type { InputHTMLAttributes, ReactNode } from "react";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  hint?: string;
  icon?: ReactNode;
}

export function Input({ label, hint, icon, className = "", id, ...props }: InputProps) {
  const inputId = id ?? props.name;

  return (
    <label className="block text-sm" htmlFor={inputId}>
      {label && (
        <span className="mb-1.5 block font-medium text-slate-700">{label}</span>
      )}
      <div className="relative">
        {icon && (
          <span className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-slate-400">
            {icon}
          </span>
        )}
        <input
          id={inputId}
          className={`w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-slate-900 shadow-sm outline-none transition-all duration-200 placeholder:text-slate-400 hover:border-slate-400 focus:border-brand focus:ring-2 focus:ring-blue-500/20 ${
            icon ? "pl-10" : ""
          } ${className}`}
          {...props}
        />
      </div>
      {hint && <span className="mt-1 block text-xs text-slate-500">{hint}</span>}
    </label>
  );
}
