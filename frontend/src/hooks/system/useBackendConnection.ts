import { useCallback, useSyncExternalStore } from "react";

import { backendConnectionService } from "@/services/backendConnectionService";

export function useBackendConnection() {
  const snapshot = useSyncExternalStore(
    (listener) => backendConnectionService.subscribe(listener),
    () => backendConnectionService.getSnapshot(),
    () => backendConnectionService.getSnapshot(),
  );

  const retry = useCallback(() => {
    void backendConnectionService.retryLastRequest();
  }, []);

  const dismiss = useCallback(() => {
    backendConnectionService.dismiss();
  }, []);

  return {
    snapshot,
    isOffline: snapshot.isOffline,
    isRetrying: snapshot.isRetrying,
    retry,
    dismiss,
  };
}
