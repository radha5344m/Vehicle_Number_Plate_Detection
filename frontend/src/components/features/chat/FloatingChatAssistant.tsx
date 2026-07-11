import { lazy, Suspense, useState } from "react";

const ChatPanel = lazy(() =>
  import("@/components/features/chat/ChatPanel").then((module) => ({
    default: module.ChatPanel,
  })),
);

export function FloatingChatAssistant() {
  const [open, setOpen] = useState(false);
  const [mounted, setMounted] = useState(false);

  function handleToggle() {
    if (!mounted) {
      setMounted(true);
      setOpen(true);
      return;
    }
    setOpen((current) => !current);
  }

  return (
    <div className="pointer-events-none fixed bottom-4 right-4 z-[60] flex flex-col items-end gap-3 sm:bottom-6 sm:right-6">
      {mounted && open ? (
        <Suspense fallback={null}>
          <div className="pointer-events-auto">
            <ChatPanel onClose={() => setOpen(false)} />
          </div>
        </Suspense>
      ) : null}

      <button
        type="button"
        onClick={handleToggle}
        className="pointer-events-auto flex h-14 w-14 items-center justify-center rounded-full bg-brand text-2xl text-white shadow-lg shadow-blue-600/30 transition hover:scale-105 hover:bg-blue-700 focus:outline-none focus:ring-4 focus:ring-brand/30"
        aria-label={open ? "Minimize Sentinel AI Assistant" : "Open Sentinel AI Assistant"}
        title="Sentinel AI Assistant"
      >
        💬
      </button>
    </div>
  );
}
