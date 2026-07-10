import { useState, type FormEvent } from "react";
import { useSearchParams } from "react-router-dom";
import { LogIn } from "lucide-react";
import { useAuth } from "@/hooks/auth/useAuth";
import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";

export function LoginForm() {
  const { login, loading, error } = useAuth();
  const [searchParams] = useSearchParams();
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [formError, setFormError] = useState<string | null>(null);
  const sessionExpired = searchParams.get("reason") === "session_expired";

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFormError(null);

    if (password.length < 8) {
      setFormError("Password must be at least 8 characters");
      return;
    }

    try {
      const redirect = searchParams.get("redirect") ?? undefined;
      const normalizedIdentifier = identifier.trim();
      const normalizedPassword = password.trim();

      if (!/^[A-Za-z0-9._-]+$/.test(normalizedIdentifier)) {
        setFormError("Use your username, employee ID, or badge number. Email addresses cannot be used to sign in.");
        return;
      }

      await login({ identifier: normalizedIdentifier, password: normalizedPassword }, redirect);
    } catch {
      // error surfaced via useAuth
    }
  }

  const displayError = formError ?? error;

  return (
    <form onSubmit={(event) => void handleSubmit(event)} className="space-y-5">
      {sessionExpired && !displayError && (
        <Alert variant="info" title="Session Expired">
          Your session has timed out. Please sign in again to continue.
        </Alert>
      )}

      <Input
        id="identifier"
        label="Username, Employee ID, or Badge Number"
        type="text"
        autoComplete="username"
        required
        value={identifier}
        onChange={(event) => setIdentifier(event.target.value)}
        placeholder="superadmin, EMP-0001, or AP001"
        hint="Sign in with username, employee ID, or badge number — not your email. New users must use the temporary password exactly as issued."
      />

      <Input
        id="password"
        label="Password"
        type="password"
        autoComplete="current-password"
        required
        minLength={8}
        value={password}
        onChange={(event) => setPassword(event.target.value)}
        placeholder="••••••••"
      />

      {displayError && (
        <Alert variant="error" title="Authentication Failed">
          {displayError}
        </Alert>
      )}

      <Button
        type="submit"
        loading={loading}
        icon={<LogIn className="h-4 w-4" />}
        className="w-full"
      >
        Sign In
      </Button>
    </form>
  );
}
