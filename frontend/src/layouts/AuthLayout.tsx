import type { ReactNode } from "react";
import { Activity, ShieldCheck } from "lucide-react";

interface AuthLayoutProps {
  children: ReactNode;
}

export function AuthLayout({ children }: AuthLayoutProps) {
  return (
    <div className="command-grid-bg relative flex min-h-screen items-center justify-center overflow-hidden bg-canvas px-4 text-slate-900">
      <div className="pointer-events-none absolute inset-0 bg-gradient-to-br from-blue-50 via-transparent to-teal-50" />
      <div className="pointer-events-none absolute -top-24 left-1/2 h-72 w-72 -translate-x-1/2 rounded-full bg-blue-100/50 blur-3xl" />

      <div className="relative w-full max-w-md animate-slide-up">
        <div className="mb-8 text-center">
          <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-brand text-white shadow-soft-lg animate-pulse-glow">
            <ShieldCheck className="h-7 w-7" aria-hidden />
          </div>
          <p className="mb-2 text-xs font-semibold uppercase tracking-[0.2em] text-brand">
            Prakasam Police Hackathon
          </p>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900">
            SentinelANPR AI - Secure Police Login
          </h1>
          <p className="mt-2 flex items-center justify-center gap-1.5 text-sm text-slate-500">
            <Activity className="h-3.5 w-3.5 text-secondary" aria-hidden />
            Unified access for super admins, station admins, and police officers
          </p>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-soft-lg sm:p-8">
          {children}
        </div>

        <p className="mt-6 text-center text-xs text-slate-400">
          Authorized personnel only · All activity is logged
        </p>
      </div>
    </div>
  );
}
