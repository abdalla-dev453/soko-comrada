import { Link } from "react-router-dom";

import { Logo } from "../common/Logo";

const COLUMNS = [
  {
    heading: "Product",
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
      { to: "/privacy", label: "Privacy" },
      { to: "/terms", label: "Terms" },
    ],
  },
];

export function Footer() {
  return (
    <footer className="bg-surface-raised">
      <div className="mx-auto max-w-6xl px-4 py-12 sm:px-6">
        <div className="grid gap-10 sm:grid-cols-2 md:grid-cols-3">
          <div>
            <Logo />
            <p className="mt-3 text-sm text-ink-muted max-w-xs">
              The campus gig board for students who'd rather find work between lectures.
            </p>
          </div>
          {COLUMNS.map((col) => (
            <div key={col.heading}>
              <h3 className="text-sm font-medium text-ink mb-3">{col.heading}</h3>
              <ul className="space-y-2">
                {col.links.map((link) => (
                  <li key={link.to}>
                    <Link
                      to={link.to}
                      className="text-sm text-ink-muted hover:text-ink transition-colors"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-10 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-xs text-ink-muted">
            &copy; {new Date().getFullYear()} Comrade Plug. Pilot campus: MUT, Murang'a County, Kenya.
          </p>
          <p className="text-xs text-ink-muted">
            hello@comradeplug.app
          </p>
        </div>
      </div>
    </footer>
  );
}