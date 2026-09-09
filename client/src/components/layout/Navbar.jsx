import { useEffect, useState } from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";
import { Menu, Moon, Sun, LogOut } from "lucide-react";
import clsx from "clsx";

import { Logo } from "../common/Logo";
import { Button } from "../common/Button";
import { useAuth } from "../../hooks/useAuth";
import { useTheme } from "../../hooks/useTheme";
import { trackCtaClick } from "../../utils/analytics";

const NAV_LINKS = [
  { to: "/gigs", label: "Browse gigs" },
  { to: "/about", label: "About" },
  { to: "/contact", label: "Contact" },
];

export function Navbar({ onOpenDrawer }) {
  const [scrolled, setScrolled] = useState(false);
  const { isAuthenticated, user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header
      className={clsx(
        "sticky top-0 z-40 transition-shadow duration-200",
        scrolled
          ? "bg-surface/80 backdrop-blur-nav shadow-card border-b border-border"
          : "bg-transparent border-b border-transparent"
      )}
    >
      <nav
        className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3 sm:px-6"
        aria-label="Primary"
      >
        <Link to="/" className="rounded-md" aria-label="Soko Comrada home">
          <Logo />
        </Link>

        <div className="hidden md:flex items-center gap-1">
          {NAV_LINKS.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) =>
                clsx(
                  "px-3.5 py-2 rounded-lg text-fluid-sm font-medium transition-colors",
                  isActive ? "text-ink bg-ink/5" : "text-ink-muted hover:text-ink hover:bg-ink/5"
                )
              }
            >
              {link.label}
            </NavLink>
          ))}
        </div>

        <div className="hidden md:flex items-center gap-2">
          <button
            type="button"
            onClick={toggleTheme}
            aria-label={theme === "dark" ? "Switch to light theme" : "Switch to dark theme"}
            className="rounded-full p-2 text-ink-muted hover:text-ink hover:bg-ink/5 transition-colors"
          >
            {theme === "dark" ? (
              <Sun className="h-4.5 w-4.5" aria-hidden="true" />
            ) : (
              <Moon className="h-4.5 w-4.5" aria-hidden="true" />
            )}
          </button>

          {isAuthenticated ? (
            <>
              <Link
                to="/dashboard"
                className="px-3.5 py-2 rounded-lg text-fluid-sm font-medium text-ink-muted hover:text-ink hover:bg-ink/5 transition-colors"
              >
                Hi, {user?.name?.split(" ")[0]}
              </Link>
              <Button
                variant="ghost"
                size="sm"
                icon={LogOut}
                onClick={() => {
                  logout();
                  navigate("/");
                }}
              >
                Log out
              </Button>
              <Button
                size="sm"
                onClick={() => {
                  trackCtaClick("post_a_gig_nav");
                  navigate("/gigs/new");
                }}
              >
                Post a gig
              </Button>
            </>
          ) : (
            <>
              <Link
                to="/login"
                className="px-3.5 py-2 rounded-lg text-fluid-sm font-medium text-ink-muted hover:text-ink hover:bg-ink/5 transition-colors"
              >
                Log in
              </Link>
              <Button
                size="sm"
                onClick={() => {
                  trackCtaClick("register_nav");
                  navigate("/register");
                }}
              >
                Join free
              </Button>
            </>
          )}
        </div>

        <button
          type="button"
          onClick={onOpenDrawer}
          aria-label="Open menu"
          className="md:hidden rounded-lg p-2 text-ink hover:bg-ink/5 transition-colors"
        >
          <Menu className="h-6 w-6" aria-hidden="true" />
        </button>
      </nav>
    </header>
  );
}