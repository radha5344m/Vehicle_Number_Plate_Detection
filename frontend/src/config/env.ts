/**
 * Environment configuration loaded from Vite env vars.
 */
export const env = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL ?? "",
  appEnv: import.meta.env.VITE_APP_ENV ?? "development",
} as const;
