import type { ReactNode } from "react";

import { BackendOfflineDialog } from "@/components/system/BackendOfflineDialog";
import { useBackendConnection } from "@/hooks/system/useBackendConnection";

interface BackendConnectionProviderProps {
  children: ReactNode;
}

export function BackendConnectionProvider({ children }: BackendConnectionProviderProps) {
  const { isOffline, isRetrying, retry, dismiss } = useBackendConnection();

  return (
    <>
      {children}
      {isOffline ? (
        <BackendOfflineDialog isRetrying={isRetrying} onRetry={retry} onDismiss={dismiss} />
      ) : null}
    </>
  );
}
