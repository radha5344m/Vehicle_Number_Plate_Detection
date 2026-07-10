import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { AlertCircle, CheckCircle2, Info, X, AlertTriangle } from "lucide-react";

type ToastVariant = "success" | "error" | "warning" | "info";

interface ToastItem {
  id: string;
  variant: ToastVariant;
  title?: string;
  message: string;
}

interface ToastContextValue {
  showToast: (toast: Omit<ToastItem, "id">) => void;
  success: (message: string, title?: string) => void;
  error: (message: string, title?: string) => void;
  warning: (message: string, title?: string) => void;
  info: (message: string, title?: string) => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

const iconMap = {
  success: CheckCircle2,
  error: AlertCircle,
  warning: AlertTriangle,
  info: Info,
};

const accentMap = {
  success: "text-green-500",
  error: "text-red-500",
  warning: "text-amber-500",
  info: "text-brand",
};

const barMap = {
  success: "bg-green-500",
  error: "bg-red-500",
  warning: "bg-amber-500",
  info: "bg-brand",
};

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<ToastItem[]>([]);

  const dismiss = useCallback((id: string) => {
    setToasts((current) => current.filter((toast) => toast.id !== id));
  }, []);

  const showToast = useCallback(
    (toast: Omit<ToastItem, "id">) => {
      const id = crypto.randomUUID();
      setToasts((current) => [...current, { ...toast, id }]);
      window.setTimeout(() => dismiss(id), 5000);
    },
    [dismiss],
  );

  const value = useMemo<ToastContextValue>(
    () => ({
      showToast,
      success: (message, title) => showToast({ variant: "success", message, title }),
      error: (message, title) => showToast({ variant: "error", message, title }),
      warning: (message, title) => showToast({ variant: "warning", message, title }),
      info: (message, title) => showToast({ variant: "info", message, title }),
    }),
    [showToast],
  );

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div
        className="pointer-events-none fixed right-4 top-4 z-[100] flex w-full max-w-sm flex-col gap-2.5"
        aria-live="polite"
        aria-atomic="true"
      >
        {toasts.map((toast) => {
          const Icon = iconMap[toast.variant];
          return (
            <div
              key={toast.id}
              className="pointer-events-auto animate-slide-up relative flex items-start gap-3 overflow-hidden rounded-xl border border-slate-200 bg-white p-4 pl-5 shadow-soft-lg"
              role="status"
            >
              <span className={`absolute inset-y-0 left-0 w-1.5 ${barMap[toast.variant]}`} />
              <Icon className={`mt-0.5 h-5 w-5 shrink-0 ${accentMap[toast.variant]}`} aria-hidden />
              <div className="min-w-0 flex-1">
                {toast.title && (
                  <p className="text-sm font-semibold text-slate-900">{toast.title}</p>
                )}
                <p className={`text-sm text-slate-600 ${toast.title ? "mt-0.5" : ""}`}>
                  {toast.message}
                </p>
              </div>
              <button
                type="button"
                onClick={() => dismiss(toast.id)}
                className="shrink-0 rounded-md p-1 text-slate-400 transition hover:bg-slate-100 hover:text-slate-600"
                aria-label="Dismiss notification"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          );
        })}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast(): ToastContextValue {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error("useToast must be used within ToastProvider");
  }
  return context;
}
