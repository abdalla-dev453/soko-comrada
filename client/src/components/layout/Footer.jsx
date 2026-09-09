import { Link } from "react-router-dom";

import { Logo } from "../common/Logo";

const COLUMNS = [
  {
    heading: "Platform",
    links: [
      { to: "/gigs", label: "Browse gigs" },
      { to: "/gigs/new", label: "Post a gig" },
      { to: "/dashboard", label: "Dashboard" },
    ],
  },
  {
    heading: "Company",
    links: [
      { to: "/about", label: "About" },
      { to: "/contact", label: "Contact" },
    ],
  },
  {
    heading: "Legal",
    links: [
      { to: "/privacy", label: "Privacy policy" },
      { to: "/terms", label: "Terms of service" },
    ],
  },
];

export function Footer() {
  return (
    <footer className="border-t border-border bg-surface mt-24 pb-20 md:pb-0">
      <div className="mx-auto max-w-6xl px-4 py-12 sm:px-6">
        <div className="grid gap-10 sm:grid-cols-2 md:grid-cols-4">
          <div>
            <Logo />
            <p className="mt-3 text-fluid-sm text-ink-muted max-w-xs">
              The campus gig board for students who'd rather find work between lectures
              than scroll five WhatsApp groups.
            </p>
          </div>

          {COLUMNS.map((col) => (
            <div key={col.heading}>
              <h3 className="text-fluid-sm font-medium text-ink mb-3">{col.heading}</h3>
              <ul className="space-y-2">
                {col.links.map((link) => (
                  <li key={link.to}>
                    <Link
                      to={link.to}
                      className="text-fluid-sm text-ink-muted hover:text-ink transition-colors"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-10 pt-6 border-t border-border flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-fluid-xs text-ink-muted">
            © {new Date().getFullYear()} Comrade Plug. Built for one campus at a time.
          </p>
          <p className="text-fluid-xs text-ink-muted">
            MUT - MURANG'A pilot — <a href="mailto:hello@sokocomrada.app" className="underline decoration-dotted">hello@sokocomrada.app</a>
          </p>
        </div>
      </div>
    </footer>
  );
}