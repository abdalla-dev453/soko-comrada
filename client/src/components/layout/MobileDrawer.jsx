import { AnimatePresence, motion } from "framer-motion";
import { NavLink, useNavigate } from "react-router-dom";
import { X, Moon, Sun, LogOut } from "lucide-react";
import clsx from "clsx";

import { Logo } from "../common/Logo";
import { Button } from "../common/Button";
import { useAuth } from "../../hooks/useAuth";
import { useTheme } from "../../hooks/useTheme";
import { slideInPanel } from "../../utils/motion";

const NAV_LINKS = [
  { to: "/gigs", label: "Browse gigs" },
  { to: "/about", label: "About" },
  { to: "/contact", label: "Contact" },
  { to: "/dashboard", label: "Dashboard", authOnly: true },
];

export function MobileDrawer({ open, onClose }) {
  const { isAuthenticated, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();

  const goTo = (path) => {
    onClose();
    navigate(path);
  };

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 bg-ink/50 md:hidden"
            onClick={onClose}
            aria-hidden="true"
          />
          <motion.aside
            variants={slideInPanel}
            initial="hidden"
            animate="show"
            exit="exit"
            role="dialog"
            aria-modal="true"
            aria-label="Menu"
            className="fixed inset-y-0 right-0 z-50 w-[82vw] max-w-xs bg-surface-raised shadow-popover md:hidden flex flex-col"
          >
            <div className="flex items-center justify-between px-5 py-4 border-b border-border">
              <Logo />
              <button
                type="button"
                onClick={onClose}
                aria-label="Close menu"
                className="rounded-full p-2 text-ink-muted hover:text-ink hover:bg-ink/5"
              >
                <X className="h-5 w-5" aria-hidden="true" />
              </button>
            </div>

            <nav className="flex-1 overflow-y-auto px-3 py-4" aria-label="Mobile">
              {NAV_LINKS.filter((link) => !link.authOnly || isAuthenticated).map((link) => (
                <NavLink
                  key={link.to}
                  to={link.to}
                  onClick={onClose}
                  className={({ isActive }) =>
                    clsx(
                      "block rounded-lg px-4 py-3 text-fluid-base font-medium transition-colors",
                      isActive ? "bg-ink/5 text-ink" : "text-ink-muted hover:bg-ink/5 hover:text-ink"
                    )
                  }
                >
                  {link.label}
                </NavLink>
              ))}

              <button
                type="button"
                onClick={toggleTheme}
                className="mt-1 flex w-full items-center gap-3 rounded-lg px-4 py-3 text-fluid-base font-medium text-ink-muted hover:bg-ink/5 hover:text-ink transition-colors"
              >
                {theme === "dark" ? (
                  <Sun className="h-5 w-5" aria-hidden="true" />
                ) : (
                  <Moon className="h-5 w-5" aria-hidden="true" />
                )}
                {theme === "dark" ? "Light theme" : "Dark theme"}
              </button>
            </nav>

            <div className="px-5 py-4 border-t border-border flex flex-col gap-2">
              {isAuthenticated ? (
                <Button
                  variant="secondary"
                  icon={LogOut}
                  onClick={() => {
                    logout();
                    goTo("/");
                  }}
                >
                  Log out
                </Button>
              ) : (
                <>
                  <Button onClick={() => goTo("/register")}>Join free</Button>
                  <Button variant="secondary" onClick={() => goTo("/login")}>
                    Log in
                  </Button>
                </>
              )}
            </div>
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  );
}