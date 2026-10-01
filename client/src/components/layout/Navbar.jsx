import clsx from "clsx";
import { AnimatePresence, motion } from "framer-motion";
import { Bookmark, LogOut, Menu, Moon, Sun } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";

import { useAuth } from "../../hooks/useAuth";
import { useTheme } from "../../hooks/useTheme";
import { trackCtaClick } from "../../utils/analytics";
import { Button } from "../common/Button";
import { Logo } from "../common/Logo";

const NAV_LINKS = [
  { to: "/", label: "Explore" },
  { to: "/about", label: "About" },
  { to: "/contact", label: "Contact" },
];

const navContainer = {
  hidden: {},
  show: {
    transition: {
      delayChildren: 0.08,
      staggerChildren: 0.06,
    },
  },
};

const navItem = {
  hidden: { opacity: 0, y: -8 },
  show: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.45, ease: [0.16, 1, 0.3, 1] },
  },
};

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
        "sticky top-0 z-40 transition-[background-color,backdrop-filter,border-color,box-shadow] duration-500",
        scrolled
          ? "bg-surface/95 backdrop-blur-sm shadow-card"
          : "bg-surface",
      )}
    >
      <motion.nav
        initial="hidden"
        animate="show"
        variants={navContainer}
        className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3 sm:px-6"
        aria-label="Primary"
      >
        <motion.div
          variants={navItem}
          whileHover={{ y: -1 }}
          whileTap={{ scale: 0.98 }}
        >
          <Link to="/" className="rounded-md" aria-label="CampusGig Kenya home">
            <Logo />
          </Link>
        </motion.div>

        <motion.div
          variants={navContainer}
          className="hidden md:flex items-center gap-1"
        >
          {NAV_LINKS.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.to === "/"}
              className="group relative rounded-button px-3.5 py-2 text-sm font-medium transition-colors"
            >
              {({ isActive }) => (
                <motion.span variants={navItem} className="relative block">
                  <span
                    className={clsx(
                      "relative z-10 transition-colors duration-200",
                      isActive
                        ? "text-brand-700"
                        : "text-text-secondary group-hover:text-brand-700",
                    )}
                  >
                    {link.label}
                  </span>
                  {isActive && (
                    <motion.span
                      layoutId="navbar-active-link"
                      className="absolute -inset-x-2 -inset-y-1 -z-0 rounded-button bg-brand-500/10"
                      transition={{
                        type: "spring",
                        stiffness: 420,
                        damping: 30,
                      }}
                    />
                  )}
                </motion.span>
              )}
            </NavLink>
          ))}
        </motion.div>

        <motion.div
          variants={navContainer}
          className="hidden md:flex items-center gap-2"
        >
          <motion.button
            type="button"
            onClick={toggleTheme}
            aria-label={
              theme === "dark"
                ? "Switch to light theme"
                : "Switch to dark theme"
            }
            whileHover={{ rotate: 8, scale: 1.08 }}
            whileTap={{ scale: 0.92 }}
            className="rounded-full p-2 text-text-secondary transition-colors hover:bg-canvas hover:text-brand-700"
          >
            <AnimatePresence initial={false} mode="wait">
              <motion.span
                key={theme}
                initial={{ opacity: 0, rotate: -90, scale: 0.5 }}
                animate={{ opacity: 1, rotate: 0, scale: 1 }}
                exit={{ opacity: 0, rotate: 90, scale: 0.5 }}
                transition={{ duration: 0.2, ease: "easeOut" }}
                className="block"
              >
                {theme === "dark" ? (
                  <Sun className="h-5 w-5" aria-hidden="true" />
                ) : (
                  <Moon className="h-5 w-5" aria-hidden="true" />
                )}
              </motion.span>
            </AnimatePresence>
          </motion.button>

          {isAuthenticated ? (
            <>
              <Link
                to="/saved"
                className="px-3.5 py-2 rounded-button text-sm font-medium text-text-secondary hover:text-brand-700 hover:bg-canvas transition-colors flex items-center gap-1.5"
              >
                <Bookmark className="h-4 w-4" aria-hidden="true" />
                Saved
              </Link>
              <Link
                to="/dashboard"
                className="px-3.5 py-2 rounded-button text-sm font-medium text-text-secondary hover:text-brand-700 hover:bg-canvas transition-colors"
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
              {user?.user_type === "employer" && (
                <Button
                  size="sm"
                  onClick={() => {
                    trackCtaClick("post_a_gig_nav");
                    navigate("/dashboard/post");
                  }}
                >
                  Post an opportunity
                </Button>
              )}
            </>
          ) : (
            <>
              <Link
                to="/login"
                className="px-3.5 py-2 rounded-button text-sm font-medium text-text-secondary hover:text-brand-700 hover:bg-canvas transition-colors"
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
        </motion.div>

        <motion.button
          type="button"
          onClick={onOpenDrawer}
          aria-label="Open menu"
          whileHover={{ scale: 1.06 }}
          whileTap={{ scale: 0.92 }}
          className="md:hidden rounded-button p-2 text-text-secondary hover:bg-canvas transition-colors"
        >
          <Menu className="h-6 w-6" aria-hidden="true" />
        </motion.button>
      </motion.nav>
    </header>
  );
}
