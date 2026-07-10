import { ShieldAlert } from "lucide-react";
import { Link } from "react-router-dom";

import { BackButton } from "@/components/ui/BackButton";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { getCurrentSession } from "@/lib/rbac";
import { PATHS } from "@/routes/paths";

export function AccessDeniedPage() {
  const session = getCurrentSession();

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-canvas px-4 py-8">
      <div className="mb-4 w-full max-w-xl">
        <BackButton />
      </div>
      <Card
        title="Access Denied"
        icon={<ShieldAlert className="h-5 w-5 text-red-500" />}
        className="w-full max-w-xl"
      >
        <div className="space-y-4">
          <p className="text-sm leading-relaxed text-slate-600">
            Your account does not have permission to open this page.
            {session ? ` Signed in as ${session.role.replaceAll("_", " ")}.` : ""}
          </p>
          <div className="flex flex-col gap-3 sm:flex-row">
            <Link to={PATHS.DASHBOARD} className="w-full sm:w-auto">
              <Button className="w-full">Go to Dashboard</Button>
            </Link>
            <Link to={PATHS.LOGIN} className="w-full sm:w-auto">
              <Button variant="secondary" className="w-full">
                Switch Account
              </Button>
            </Link>
          </div>
        </div>
      </Card>
    </div>
  );
}
