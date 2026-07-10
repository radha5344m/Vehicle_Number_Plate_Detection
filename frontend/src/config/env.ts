/**
 * Environment configuration loaded from Vite env vars.
 *
 * Local dev: leave ``VITE_API_BASE_URL`` empty — Vite proxies ``/v1`` to the API.
 * Split production deploy: set ``VITE_API_BASE_URL`` to the backend URL at build time.
 * Combined deploy (API serves the SPA): leave empty — requests use the same origin.
 */
function normalizeBaseUrl(value: string | undefined): string {
  return (value ?? "").trim().replace(/\/$/, "");
}

export const env = {
  apiBaseUrl: normalizeBaseUrl(import.meta.env.VITE_API_BASE_URL),
  appEnv: import.meta.env.VITE_APP_ENV ?? "development",
  isProduction: import.meta.env.PROD,
} as const;
