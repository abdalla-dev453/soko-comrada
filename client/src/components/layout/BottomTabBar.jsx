import { NavLink } from "react-router-dom";
import { Home, PlusCircle, Bell, User } from "lucide-react";
import clsx from "clsx";

import { useAuth } from "../../hooks/useAuth";

const TABS = [
  { to: "/", label: "Home", icon: Home, end: true },
  { to: "/gigs/new", label: "Post", icon: PlusCircle, authOnly: true },
  { to: "/notifications", label: "Alerts", icon: Bell, authOnly: true },
  { to: "/dashboard", label: "Profile", icon: User, authOnly: true },
];

export function BottomTabBar() {
  const { isAuthenticated } = useAuth();

  return (
    <nav
      aria-label="Primary mobile"
      className="fixed inset-x-0 bottom-0 z-40 border-t border-border bg-surface/90 backdrop-blur-nav md:hidden"
      style={{ paddingBottom: "env(safe-area-inset-bottom)" }}
    >
      <ul className="grid grid-cols-4">
        {TABS.map((tab) => {
          const Icon = tab.icon;
          const to = tab.authOnly && !isAuthenticated ? "/login" : tab.to;
          return (
            <li key={tab.label}>
              <NavLink
                to={to}
                end={tab.end}
                className={({ isActive }) =>
                  clsx(
                    "flex flex-col items-center gap-1 py-2.5 text-fluid-xs font-medium transition-colors",
                    isActive ? "text-marigold-strong" : "text-ink-muted"
                  )
                }
              >
                {({ isActive }) => (
                  <>
                    <Icon
                      className={clsx("h-5 w-5", isActive && "scale-105")}
                      strokeWidth={isActive ? 2.4 : 2}
                      aria-hidden="true"
                    />
                    <span>{tab.label}</span>
                  </>
                )}
              </NavLink>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}