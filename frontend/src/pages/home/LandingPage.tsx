import { Link, Navigate } from "react-router-dom";
import { LogIn, ShieldCheck } from "lucide-react";
import { PATHS } from "@/routes/paths";
import { isAuthenticated } from "@/stores/authStore";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";

export function LandingPage() {
  const authenticated = isAuthenticated();

  if (authenticated) {
    return <Navigate to={PATHS.DASHBOARD} replace />;
  }

  return (
    <div className="command-grid-bg relative min-h-screen overflow-hidden bg-canvas text-slate-900">
      <div className="pointer-events-none absolute inset-0 bg-gradient-to-b from-blue-50 via-transparent to-teal-50/60" />
      <div className="pointer-events-none absolute -top-32 left-1/2 h-96 w-96 -translate-x-1/2 rounded-full bg-blue-100/50 blur-3xl" />

      <div className="relative mx-auto flex min-h-screen max-w-5xl flex-col items-center justify-center px-4 py-16">
        <div className="animate-slide-up text-center">
          <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-brand text-white shadow-soft-lg animate-pulse-glow">
            <ShieldCheck className="h-8 w-8" aria-hidden />
          </div>

          <Badge variant="info" className="mb-4">
            Prakasam Police Hackathon
          </Badge>

          <h1 className="text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl lg:text-6xl">
            Sentinel<span className="text-brand">ANPR</span> AI
          </h1>
          <p className="mx-auto mt-4 max-w-xl text-base leading-relaxed text-slate-500 sm:text-lg">
            Vision AI-powered vehicle registration verification and cloned-plate risk analysis — a
            premium command center for public safety operations.
          </p>
        </div>

        <div className="mt-10 flex animate-fade-in flex-wrap justify-center gap-3">
          <Link to={PATHS.LOGIN}>
            <Button size="lg" icon={<LogIn className="h-4 w-4" />}>
              Officer Login
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
