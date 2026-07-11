import { KeyRound, X } from "lucide-react";
import { useState } from "react";

import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import type { UserItem } from "@/types/api/users";

interface Props {
  user: UserItem;
  onClose: () => void;
  onSubmit: (newPassword: string, confirmPassword: string) => Promise<void>;
}

export function StationAdminResetPasswordDialog({ user, onClose, onSubmit }: Props) {
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);

    if (newPassword.length < 8) {
      setError("Password must be at least 8 characters long.");
      return;
    }
    if (newPassword !== confirmPassword) {
      setError("Password and Confirm Password must match.");
      return;
    }

    setSubmitting(true);
    try {
      await onSubmit(newPassword, confirmPassword);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Password reset failed. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-3 backdrop-blur-sm sm:p-4">
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="reset-password-dialog-title"
        className="flex max-h-[90vh] w-full max-w-[95vw] flex-col overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-2xl sm:max-w-lg"
      >
        <div className="border-b border-slate-100 px-4 py-5 sm:px-6">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-start gap-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-100 text-blue-600">
                <KeyRound className="h-6 w-6" />
              </div>
              <div>
                <h2 id="reset-password-dialog-title" className="text-xl font-semibold text-slate-900">
                  Reset Password
                </h2>
                <p className="mt-1 text-sm text-slate-600">
                  Set a new temporary password for this Police Station Admin.
                </p>
              </div>
            </div>
            <button
              type="button"
              onClick={onClose}
              className="rounded-lg p-2 text-slate-400 transition hover:bg-slate-100 hover:text-slate-600"
              aria-label="Close"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>

        <form className="space-y-5 overflow-y-auto px-4 py-5 sm:px-6" onSubmit={(event) => void handleSubmit(event)}>
          {error && (
            <Alert variant="error" title="Validation Error">
              {error}
            </Alert>
          )}

          <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-4 text-sm text-slate-700">
            <div className="grid gap-2">
              <div>
                <span className="font-medium text-slate-900">Police Station:</span> {user.police_station}
              </div>
              <div>
                <span className="font-medium text-slate-900">Username:</span> {user.username}
              </div>
            </div>
          </div>

          <Input
            label="New Password"
            type="password"
            value={newPassword}
            onChange={(event) => setNewPassword(event.target.value)}
            required
            minLength={8}
            autoComplete="new-password"
          />
          <Input
            label="Confirm Password"
            type="password"
            value={confirmPassword}
            onChange={(event) => setConfirmPassword(event.target.value)}
            required
            minLength={8}
            autoComplete="new-password"
          />

          <div className="flex flex-wrap gap-2">
            <Button type="submit" disabled={submitting}>
              {submitting ? "Resetting..." : "Reset Password"}
            </Button>
            <Button type="button" variant="secondary" onClick={onClose} disabled={submitting}>
              Cancel
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
