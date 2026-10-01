import { NavLink } from "react-router-dom";
import { Home, Bookmark, Send, MessageCircle, User } from "lucide-react";
import clsx from "clsx";

import { useAuth } from "../../hooks/useAuth";

const TABS = [
  { to: "/", label: "Explore", icon: Home, end: true },
  { to: "/saved", label: "Saved", icon: Bookmark, authOnly: true },
  { to: "/dashboard/applications", label: "Applications", icon: Send, authOnly: true },
  { to: "/messages", label: "Messages", icon: MessageCircle, authOnly: true },
  { to: "/profile", label: "Profile", icon: User, authOnly: true },
];

export function BottomTabBar() {
  const { isAuthenticated } = useAuth();

  return (
    <nav
      aria-label="Primary mobile"
      className="bottom-nav"
    >
      <ul className="grid grid-cols-5 w-full">
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
                    "bottom-nav-item",
                    isActive && "active",
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
