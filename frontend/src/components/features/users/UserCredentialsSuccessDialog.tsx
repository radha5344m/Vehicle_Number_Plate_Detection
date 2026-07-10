import { CheckCircle2, Copy, Download, Eye, EyeOff, Printer, X } from "lucide-react";
import { useState } from "react";

import { Alert } from "@/components/ui/Alert";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import {
  buildCredentialsText,
  copyText,
  downloadUserCredentialsPdf,
  formatRoleLabel,
  printUserCredentials,
  showBadgeNumber,
  type UserCredentialsDialogMode,
  type UserCredentialsRecord,
} from "@/lib/userCredentials";

interface Props {
  user: UserCredentialsRecord;
  temporaryPassword: string;
  mode?: UserCredentialsDialogMode["kind"];
  onClose: () => void;
}

export function UserCredentialsSuccessDialog({
  user,
  temporaryPassword,
  mode = "create",
  onClose,
}: Props) {
  const [passwordVisible, setPasswordVisible] = useState(false);
  const passwordLabel = mode === "reset" ? "New Temporary Password" : "Temporary Password";
  const title = mode === "reset" ? "Password Reset Successfully" : "User Created Successfully";
  const subtitle =
    mode === "reset"
      ? "A new temporary password has been generated. Please securely share these credentials with the user."
      : "The account has been created successfully. Please securely share the following credentials with the user.";

  const allCredentials = buildCredentialsText(user, temporaryPassword, { passwordLabel });

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-3 backdrop-blur-sm sm:p-4">
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="credentials-dialog-title"
        className="flex max-h-[90vh] w-full max-w-[95vw] flex-col overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-2xl sm:max-w-2xl"
      >
        <div className="border-b border-slate-100 px-4 py-5 sm:px-6">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-start gap-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-emerald-100 text-emerald-600">
                <CheckCircle2 className="h-7 w-7" />
              </div>
              <div>
                <h2 id="credentials-dialog-title" className="text-xl font-semibold text-slate-900">
                  {title}
                </h2>
                <p className="mt-1 text-sm text-slate-600">{subtitle}</p>
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

        <div className="space-y-5 overflow-y-auto px-4 py-5 sm:px-6">
          <Alert variant="success" title="Success">
            {mode === "reset"
              ? "The password has been reset and a new temporary password was generated."
              : "The user account is ready. Share the credentials below before closing this dialog."}
          </Alert>

          <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
            <div className="mb-4 flex items-center justify-between gap-3">
              <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-700">
                Login Credentials
              </h3>
              <Badge variant="info">{formatRoleLabel(user.role)}</Badge>
            </div>

            <dl className="grid gap-4 sm:grid-cols-2">
              <CredentialField label="User ID" value={user.user_id} mono />
              <CredentialField label="Username" value={user.username} mono />
              <CredentialField label="Employee ID" value={user.employee_id} mono />
              {showBadgeNumber(user.role) && user.badge_number ? (
                <CredentialField label="Badge Number" value={user.badge_number} mono />
              ) : null}
              <CredentialField label="Role" value={formatRoleLabel(user.role)} />
              <div className="sm:col-span-2">
                <dt className="text-xs font-medium uppercase tracking-wide text-slate-500">
                  {passwordLabel}
                </dt>
                <dd className="mt-1 flex items-center gap-2">
                  <span className="flex-1 rounded-xl border border-slate-200 bg-white px-3 py-2.5 font-mono text-sm text-slate-900">
                    {passwordVisible ? temporaryPassword : "•".repeat(Math.min(temporaryPassword.length, 16))}
                  </span>
                  <Button
                    type="button"
                    variant="secondary"
                    size="sm"
                    icon={passwordVisible ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    onClick={() => setPasswordVisible((current) => !current)}
                  >
                    {passwordVisible ? "Hide" : "Show"}
                  </Button>
                </dd>
              </div>
            </dl>
          </div>

          <Alert variant="warning" title="Important">
            This temporary password will only be shown once. Please copy or print these credentials
            before closing this dialog. The user must change the password during first login.
          </Alert>
        </div>

        <div className="flex flex-col gap-2 border-t border-slate-100 px-4 py-5 sm:flex-row sm:flex-wrap sm:px-6">
          <Button
            className="w-full sm:w-auto"
            icon={<Copy className="h-4 w-4" />}
            onClick={() => void copyText(allCredentials)}
          >
            Copy All Credentials
          </Button>
          <Button
            className="w-full sm:w-auto"
            variant="secondary"
            icon={<Copy className="h-4 w-4" />}
            onClick={() => void copyText(user.username)}
          >
            Copy Username
          </Button>
          <Button
            className="w-full sm:w-auto"
            variant="secondary"
            icon={<Copy className="h-4 w-4" />}
            onClick={() => void copyText(temporaryPassword)}
          >
            Copy Password
          </Button>
          <Button
            className="w-full sm:w-auto"
            variant="secondary"
            icon={<Printer className="h-4 w-4" />}
            onClick={() => printUserCredentials(user, temporaryPassword, { passwordLabel })}
          >
            Print Credentials
          </Button>
          <Button
            className="w-full sm:w-auto"
            variant="secondary"
            icon={<Download className="h-4 w-4" />}
            onClick={() => downloadUserCredentialsPdf(user, temporaryPassword, { passwordLabel })}
          >
            Download Credentials (PDF)
          </Button>
          <Button variant="secondary" onClick={onClose}>
            Close
          </Button>
        </div>
      </div>
    </div>
  );
}

function CredentialField({
  label,
  value,
  mono = false,
}: {
  label: string;
  value: string;
  mono?: boolean;
}) {
  return (
    <div>
      <dt className="text-xs font-medium uppercase tracking-wide text-slate-500">{label}</dt>
      <dd className={`mt-1 text-sm font-medium text-slate-900 ${mono ? "font-mono" : ""}`}>{value}</dd>
    </div>
  );
}
