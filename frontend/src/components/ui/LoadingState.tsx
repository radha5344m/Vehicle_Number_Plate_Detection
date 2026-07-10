import { Spinner } from "@/components/ui/Spinner";

interface LoadingStateProps {
  label?: string;
  fullHeight?: boolean;
}

export function LoadingState({
  label = "Loading data…",
  fullHeight = false,
}: LoadingStateProps) {
  return (
    <div
      className={`flex flex-col items-center justify-center gap-4 rounded-2xl border border-dashed border-slate-300 bg-white px-8 py-16 animate-fade-in ${
        fullHeight ? "min-h-[280px]" : ""
      }`}
    >
      <Spinner size="lg" />
      <p className="text-sm text-slate-500">{label}</p>
    </div>
  );
}
