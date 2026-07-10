import { Link } from "react-router-dom";
import { Compass } from "lucide-react";
import { PATHS } from "@/routes/paths";
import { BackButton } from "@/components/ui/BackButton";
import { Button } from "@/components/ui/Button";

export function NotFoundPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-canvas px-4 py-8 text-center text-slate-900">
      <div className="mb-6 w-full max-w-sm">
        <BackButton className="mx-auto" />
      </div>
      <div className="mb-5 flex h-16 w-16 items-center justify-center rounded-2xl bg-brand-soft text-brand ring-1 ring-blue-100">
        <Compass className="h-8 w-8" aria-hidden />
      </div>
      <p className="font-mono text-sm font-semibold uppercase tracking-[0.2em] text-brand">
        Error 404
      </p>
      <h1 className="mt-2 text-2xl font-bold tracking-tight text-slate-900">Page not found</h1>
      <p className="mt-2 max-w-sm text-sm text-slate-500">
        The page you are looking for doesn’t exist or has been moved.
      </p>
      <Link to={PATHS.HOME} className="mt-6 w-full max-w-xs">
        <Button className="w-full">Back to SentinelANPR AI</Button>
      </Link>
    </div>
  );
}
