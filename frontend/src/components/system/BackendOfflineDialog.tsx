import { ServerOff } from "lucide-react";

import { Button } from "@/components/ui/Button";
import { Spinner } from "@/components/ui/Spinner";

interface BackendOfflineDialogProps {
  isRetrying: boolean;
  onRetry: () => void;
  onDismiss: () => void;
}

export function BackendOfflineDialog({ isRetrying, onRetry, onDismiss }: BackendOfflineDialogProps) {
  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center bg-slate-900/45 px-4 backdrop-blur-sm"
      role="alertdialog"
      aria-modal="true"
      aria-labelledby="backend-offline-title"
      aria-describedby="backend-offline-description"
    >
      <div className="w-full max-w-[95vw] animate-slide-up rounded-2xl border border-slate-200 bg-white p-5 shadow-soft-lg sm:max-w-md sm:p-6">
        <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-amber-50 text-amber-600">
          <ServerOff className="h-6 w-6" aria-hidden />
        </div>

        <h2 id="backend-offline-title" className="text-center text-lg font-semibold text-slate-900">
          Backend Offline
        </h2>
        <p id="backend-offline-description" className="mt-2 text-center text-sm leading-relaxed text-slate-500">
          Unable to reach the SentinelANPR backend service. Ensure the API server is running, then
          retry your request.
        </p>

        {isRetrying ? (
          <div className="mt-6 flex justify-center">
            <Spinner label="Retrying…" />
          </div>
        ) : (
          <div className="mt-6 flex flex-col gap-2 sm:flex-row sm:flex-wrap sm:justify-center">
            <Button className="w-full sm:w-auto" onClick={onRetry}>Retry</Button>
            <Button variant="secondary" onClick={onDismiss}>
              Dismiss
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
