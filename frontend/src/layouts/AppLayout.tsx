import { useEffect, useState, type ReactNode } from "react";import { Link, useLocation } from "react-router-dom";
import {
  BarChart3,
  Bell,
  BriefcaseBusiness,
  ChevronRight,
  FileText,
  FileWarning,
  History,
  LayoutDashboard,
  LogOut,
  Menu,
  ShieldCheck,
  Building2,
  UserCircle,
  Users,
  X,
} from "lucide-react";
import { hasPermission, hasRole } from "@/lib/rbac";
import { PATHS } from "@/routes/paths";
import { getStoredOfficer } from "@/stores/authStore";
import { useAuth } from "@/hooks/auth/useAuth";

interface AppLayoutProps {
  children: ReactNode;
}

interface NavItem {
  to: string;
  label: string;
  icon: typeof LayoutDashboard;
}

function isDashboardAlias(pathname: string): boolean {
  return [
    PATHS.DASHBOARD,
    PATHS.ADMIN_DASHBOARD,
    PATHS.STATION_DASHBOARD,
    PATHS.OFFICER_DASHBOARD,
  ].includes(pathname as typeof PATHS.DASHBOARD);
}

function NavLink({ item, onNavigate }: { item: NavItem; onNavigate?: () => void }) {
  const location = useLocation();
  const isActive =
    location.pathname === item.to ||
    (item.to === PATHS.DASHBOARD && isDashboardAlias(location.pathname));
  const Icon = item.icon;

  return (
    <Link
      to={item.to}
      onClick={onNavigate}
      className={`group relative flex min-h-11 items-center gap-3 rounded-lg px-3 py-3 text-sm font-medium transition-all duration-200 ${
        isActive
          ? "bg-brand-soft text-brand"
          : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
      }`}
    >
      {isActive && (
        <span className="absolute left-0 top-1/2 h-5 w-1 -translate-y-1/2 rounded-r-full bg-brand" />
      )}
      <Icon
        className={`h-4 w-4 shrink-0 transition-colors ${
          isActive ? "text-brand" : "text-slate-400 group-hover:text-slate-600"
        }`}
        aria-hidden
      />
      <span className="flex-1">{item.label}</span>
      {isActive && <ChevronRight className="h-3.5 w-3.5 text-brand/70" aria-hidden />}
    </Link>
  );
}

function ClockDisplay() {
  const [time, setTime] = useState(() => new Date());

  useEffect(() => {
    const interval = window.setInterval(() => setTime(new Date()), 1000);
    return () => window.clearInterval(interval);
  }, []);

  return (
    <time className="hidden font-mono text-xs text-slate-500 md:block" dateTime={time.toISOString()}>
      {time.toLocaleString(undefined, {
        weekday: "short",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      })}
    </time>
  );
}

function initialsOf(first?: string, last?: string): string {
  const a = first?.[0] ?? "";
  const b = last?.[0] ?? "";
  return (a + b).toUpperCase() || "OF";
}

export function AppLayout({ children }: AppLayoutProps) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const { logout } = useAuth();
  const officer = getStoredOfficer();
  const navItems: NavItem[] = [];

  useEffect(() => {
    if (!mobileOpen) return;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = previousOverflow;
    };
  }, [mobileOpen]);

  if (hasPermission("dashboard")) {
    navItems.push({ to: PATHS.DASHBOARD, label: "Dashboard", icon: LayoutDashboard });
  }
  if (hasPermission("vehicle_verification")) {
    navItems.push({ to: PATHS.WORKFLOW, label: "Vehicle Verification", icon: ShieldCheck });
  }
  if (hasPermission("challans")) {
    navItems.push({ to: PATHS.ECHALLANS, label: "e-Challan", icon: FileWarning });
  }
  if (hasRole("STATION_ADMIN")) {
    navItems.push({
      to: PATHS.STATION_INVESTIGATIONS,
      label: "Station Investigations",
      icon: History,
    });
  } else if (hasPermission("investigation_history")) {
    navItems.push({
      to: PATHS.HISTORY_SCANS,
      label: hasRole("POLICE_OFFICER") ? "My Investigations" : "Investigation History",
      icon: History,
    });
  }
  if (hasPermission("reports")) {
    navItems.push({
      to: PATHS.REPORTS,
      label: hasRole("POLICE_OFFICER") ? "My Reports" : "Reports",
      icon: FileText,
    });
  }
  if (hasPermission("analytics")) {
    navItems.push({ to: PATHS.ANALYTICS, label: "Analytics", icon: BarChart3 });
  }
  if (
    (hasRole("SUPER_ADMIN") && (hasPermission("users") || hasPermission("stations"))) ||
    (hasRole("STATION_ADMIN") && hasPermission("officers"))
  ) {
    navItems.push({ to: PATHS.MANAGEMENT, label: "Management", icon: BriefcaseBusiness });
  }
  if (hasPermission("notifications") || hasRole("POLICE_OFFICER")) {
    navItems.push({ to: PATHS.NOTIFICATIONS, label: "Notifications", icon: Bell });
  }
  if (hasPermission("profile")) {
    navItems.push({ to: PATHS.PROFILE, label: "Profile", icon: UserCircle });
  }

  return (
    <div className="min-h-screen bg-canvas text-slate-900">
      {mobileOpen && (
        <button
          type="button"
          className="fixed inset-0 z-40 bg-slate-900/30 backdrop-blur-sm lg:hidden"
          onClick={() => setMobileOpen(false)}
          aria-label="Close navigation"
        />
      )}

      <aside
        className={`fixed inset-y-0 left-0 z-50 flex w-64 flex-col border-r border-slate-200 bg-white transition-transform duration-300 lg:translate-x-0 ${
          mobileOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex items-center justify-between border-b border-slate-200 px-4 py-4">
          <Link
            to={PATHS.DASHBOARD}
            className="flex items-center gap-2.5"
            onClick={() => setMobileOpen(false)}
          >
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-brand text-white shadow-sm shadow-blue-600/30">
              <ShieldCheck className="h-5 w-5" aria-hidden />
            </div>
            <div>
              <p className="text-sm font-bold tracking-tight text-slate-900">
                Sentinel<span className="text-brand">ANPR</span>
              </p>
              <p className="text-[10px] font-medium uppercase tracking-[0.15em] text-slate-400">
                Command Center
              </p>
            </div>
          </Link>
          <button
            type="button"
            className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 lg:hidden"
            onClick={() => setMobileOpen(false)}
            aria-label="Close menu"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <nav className="flex-1 space-y-6 overflow-y-auto px-3 py-5">
          <div>
            <p className="mb-2 px-3 text-[10px] font-semibold uppercase tracking-[0.15em] text-slate-400">
              Operations
            </p>
            <div className="space-y-1">
              {navItems.map((item) => (
                <NavLink key={item.to} item={item} onNavigate={() => setMobileOpen(false)} />
              ))}
            </div>
          </div>
        </nav>

        <div className="border-t border-slate-200 p-3">
          <div className="flex items-center gap-2 rounded-lg bg-slate-50 px-3 py-2.5">
            <span className="h-2 w-2 animate-pulse rounded-full bg-green-500" />
            <span className="text-xs font-medium text-slate-600">All systems operational</span>
          </div>
        </div>
      </aside>

      <div className="lg:pl-64">
        <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/85 backdrop-blur-xl">
          <div className="flex items-center justify-between gap-4 px-4 py-3 sm:px-6">
            <div className="flex items-center gap-3">
              <button
                type="button"
                className="inline-flex min-h-11 min-w-11 items-center justify-center rounded-lg border border-slate-200 text-slate-500 transition hover:bg-slate-100 lg:hidden"
                onClick={() => setMobileOpen(true)}
                aria-label="Open navigation"
              >
                <Menu className="h-5 w-5" />
              </button>
              <div className="hidden sm:block">
                <p className="text-xs font-semibold uppercase tracking-[0.15em] text-brand">
                  Prakasam Police
                </p>
                <p className="text-sm text-slate-500">ANPR Command Center</p>
              </div>
            </div>

            <div className="flex items-center gap-3 sm:gap-4">
              <ClockDisplay />

              <div className="hidden h-8 w-px bg-slate-200 sm:block" />

              <div className="flex items-center gap-3">
                <div className="flex h-9 w-9 items-center justify-center rounded-full bg-brand-soft text-sm font-bold text-brand ring-1 ring-blue-100">
                  {initialsOf(officer?.first_name, officer?.last_name)}
                </div>
                <div className="hidden text-right leading-tight sm:block">
                  <p className="text-sm font-semibold text-slate-900">
                    {officer ? `${officer.first_name} ${officer.last_name}` : "Officer"}
                  </p>
                  <p className="text-xs text-slate-500">
                    {officer ? `${officer.rank} · ${officer.badge_number}` : "Signed in"}
                  </p>
                </div>
              </div>

              <button
                type="button"
                onClick={() => void logout()}
                className="inline-flex min-h-11 items-center gap-2 rounded-lg border border-slate-200 px-3 py-2 text-sm font-medium text-slate-600 transition hover:border-red-200 hover:bg-red-50 hover:text-red-600"
              >
                <LogOut className="h-4 w-4" aria-hidden />
                <span className="hidden sm:inline">Sign Out</span>
              </button>
            </div>
          </div>
        </header>

        <main className="mx-auto max-w-7xl px-3 py-5 sm:px-6 sm:py-8">{children}</main>
      </div>
    </div>
  );
}
