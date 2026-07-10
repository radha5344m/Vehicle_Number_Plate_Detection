const GLOBAL_SINGLETON_KEY = "__sentinelBackendOfflineService__";

export interface BackendOfflineSnapshot {
  isOffline: boolean;
  isRetrying: boolean;
}

type OfflineListener = (snapshot: BackendOfflineSnapshot) => void;
type RetryAction = () => Promise<unknown>;

/**
 * Tracks backend reachability based on real API traffic only.
 * Never polls /v1/health and never retries automatically.
 */
export class BackendConnectionService {
  private listeners = new Set<OfflineListener>();
  private snapshot: BackendOfflineSnapshot = { isOffline: false, isRetrying: false };
  private pendingRetry: RetryAction | null = null;

  getSnapshot(): BackendOfflineSnapshot {
    return this.snapshot;
  }

  subscribe(listener: OfflineListener): () => void {
    this.listeners.add(listener);
    listener(this.snapshot);
    return () => {
      this.listeners.delete(listener);
    };
  }

  reportOffline(retry: RetryAction): void {
    this.pendingRetry = retry;
    if (!this.snapshot.isOffline) {
      this.setSnapshot({ isOffline: true, isRetrying: false });
    }
  }

  notifyRequestSuccess(): void {
    if (!this.snapshot.isOffline && !this.snapshot.isRetrying) {
      return;
    }
    this.pendingRetry = null;
    this.setSnapshot({ isOffline: false, isRetrying: false });
  }

  async retryLastRequest(): Promise<void> {
    if (!this.pendingRetry || this.snapshot.isRetrying) {
      return;
    }

    this.setSnapshot({ isOffline: true, isRetrying: true });

    try {
      await this.pendingRetry();
      this.pendingRetry = null;
      this.setSnapshot({ isOffline: false, isRetrying: false });
    } catch {
      this.setSnapshot({ isOffline: true, isRetrying: false });
    }
  }

  dismiss(): void {
    this.pendingRetry = null;
    this.setSnapshot({ isOffline: false, isRetrying: false });
  }

  resetForTests(): void {
    this.pendingRetry = null;
    this.snapshot = { isOffline: false, isRetrying: false };
    this.listeners.clear();
  }

  private setSnapshot(next: BackendOfflineSnapshot): void {
    this.snapshot = next;
    this.listeners.forEach((listener) => listener(this.snapshot));
  }
}

function getOrCreateService(): BackendConnectionService {
  const globalStore = globalThis as typeof globalThis & {
    [GLOBAL_SINGLETON_KEY]?: BackendConnectionService;
  };

  if (!globalStore[GLOBAL_SINGLETON_KEY]) {
    globalStore[GLOBAL_SINGLETON_KEY] = new BackendConnectionService();
  }

  return globalStore[GLOBAL_SINGLETON_KEY];
}

export const backendConnectionService = getOrCreateService();
