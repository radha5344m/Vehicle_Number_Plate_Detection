import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "@/hooks/auth/useAuth";
import { authService } from "@/services/authService";
import type { MeResponse } from "@/types/api/auth";
import { PATHS } from "@/routes/paths";

export function ProtectedPage() {
  const { officer, logout } = useAuth();
  const [profile, setProfile] = useState<MeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    authService
      .me()
      .then(setProfile)
      .catch(() => setError("Failed to load protected profile"));
  }, []);

  return (
    <div className="min-h-screen bg-canvas text-slate-900">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-3xl items-center justify-between px-4 py-4">
          <Link to={PATHS.HOME} className="text-lg font-semibold tracking-tight">
            Sentinel<span className="text-brand">ANPR</span>
          </Link>
          <button
            type="button"
            onClick={() => void logout()}
            className="rounded-lg border border-slate-200 px-3 py-1.5 text-sm text-slate-600 transition hover:border-red-200 hover:bg-red-50 hover:text-red-600"
          >
            Logout
          </button>
        </div>
      </header>

      <main className="mx-auto max-w-3xl px-4 py-10">
        <h1 className="text-2xl font-bold tracking-tight">Protected Area</h1>
        <p className="mt-1 text-sm text-slate-500">
          This page requires a valid JWT from the authentication module.
        </p>

        {error && (
          <p className="mt-6 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-700">
            {error}
          </p>
        )}

        {officer && (
          <div className="mt-8 rounded-2xl border border-slate-200 bg-white p-6 shadow-soft">
            <h2 className="text-sm font-medium text-slate-500">Signed in as</h2>
            <p className="mt-2 text-xl font-semibold">
              {officer.first_name} {officer.last_name}
            </p>
            <p className="mt-1 text-sm text-slate-500">
              {officer.rank} · Badge {officer.badge_number} · Station {officer.station_code}
            </p>
          </div>
        )}

        {profile && (
          <div className="mt-6 rounded-2xl border border-green-200 bg-white p-6 shadow-soft ring-1 ring-green-100">
            <h2 className="text-sm font-medium text-green-600">Verified via GET /v1/auth/me</h2>
            <p className="mt-2 text-sm text-slate-700">
              Session: <span className="font-mono text-slate-500">{profile.session_id}</span>
            </p>
            <p className="mt-2 text-sm text-slate-700">
              Permissions: {profile.permissions.join(", ") || "none"}
            </p>
          </div>
        )}
      </main>
    </div>
  );
}
