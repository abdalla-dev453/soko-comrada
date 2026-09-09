import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Star, Briefcase, ClipboardList, PlusCircle } from "lucide-react";
import clsx from "clsx";

import { SEO } from "../components/common/SEO";
import { Button } from "../components/common/Button";
import { EmptyState } from "../components/common/EmptyState";
import { SectionLoader } from "../components/common/Loader";
import { GigCard } from "../components/gigs/GigCard";
import { fetchMyApplications, fetchMyGigs } from "../api/gigs";
import { useAuth } from "../hooks/useAuth";

const STATUS_STYLES = {
  PENDING: "bg-ink/5 text-ink-muted",
  ACCEPTED: "bg-moss-soft text-moss-strong",
  REJECTED: "bg-coral-soft text-coral-strong",
};

export default function Dashboard() {
  const { user } = useAuth();
  const [tab, setTab] = useState("gigs");
  const [gigs, setGigs] = useState(null);
  const [applications, setApplications] = useState(null);

  useEffect(() => {
    fetchMyGigs().then(setGigs).catch(() => setGigs([]));
    fetchMyApplications().then(setApplications).catch(() => setApplications([]));
  }, []);

  return (
    <>
      <SEO title="Dashboard" description="Your posted gigs and applications on Soko Comrada." path="/dashboard" noindex />

      <div className="mx-auto max-w-5xl px-4 py-10 sm:px-6">
        <div className="mb-8 flex flex-wrap items-end justify-between gap-4">
          <div>
            <h1 className="font-display font-semibold text-fluid-2xl">
              Hi, {user?.name?.split(" ")[0]}
            </h1>
            <p className="mt-1 text-fluid-sm text-ink-muted flex items-center gap-3">
              {user?.campus_location}
              {user?.avg_rating != null && (
                <span className="inline-flex items-center gap-1">
                  <Star className="h-3.5 w-3.5 fill-marigold text-marigold" aria-hidden="true" />
                  {user.avg_rating.toFixed(1)}
                </span>
              )}
            </p>
          </div>
          <Button as={Link} to="/gigs/new" icon={PlusCircle}>
            Post a gig
          </Button>
        </div>

        <div className="flex gap-1 border-b border-border mb-6">
          <TabButton active={tab === "gigs"} onClick={() => setTab("gigs")} icon={Briefcase}>
            My gigs {gigs && `(${gigs.length})`}
          </TabButton>
          <TabButton active={tab === "applications"} onClick={() => setTab("applications")} icon={ClipboardList}>
            My applications {applications && `(${applications.length})`}
          </TabButton>
        </div>

        {tab === "gigs" && (
          <>
            {gigs === null && <SectionLoader label="Loading your gigs…" />}
            {gigs && gigs.length === 0 && (
              <EmptyState
                icon={Briefcase}
                title="You haven't posted a gig yet"
                description="Need something done on campus? Post it and start getting applicants."
                action={
                  <Button as={Link} to="/gigs/new">
                    Post your first gig
                  </Button>
                }
              />
            )}
            {gigs && gigs.length > 0 && (
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {gigs.map((gig) => (
                  <GigCard key={gig.id} gig={gig} />
                ))}
              </div>
            )}
          </>
        )}

        {tab === "applications" && (
          <>
            {applications === null && <SectionLoader label="Loading your applications…" />}
            {applications && applications.length === 0 && (
              <EmptyState
                icon={ClipboardList}
                title="No applications yet"
                description="Browse open gigs on your campus and apply to the ones that fit."
                action={
                  <Button as={Link} to="/gigs">
                    Browse gigs
                  </Button>
                }
              />
            )}
            {applications && applications.length > 0 && (
              <ul className="flex flex-col gap-3">
                {applications.map((app) => (
                  <li
                    key={app.id}
                    className="flex items-center justify-between gap-4 rounded-lg border border-border bg-surface p-4"
                  >
                    <div>
                      <Link
                        to={`/gigs/${app.gig_id}`}
                        className="font-medium text-fluid-sm text-ink hover:underline decoration-dotted"
                      >
                        View gig #{app.gig_id}
                      </Link>
                      {app.proposal_text && (
                        <p className="mt-1 text-fluid-sm text-ink-muted line-clamp-1">
                          {app.proposal_text}
                        </p>
                      )}
                    </div>
                    <span
                      className={clsx(
                        "flex-shrink-0 rounded-full px-2.5 py-1 text-fluid-xs font-medium",
                        STATUS_STYLES[app.status]
                      )}
                    >
                      {app.status}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </>
        )}
      </div>
    </>
  );
}

function TabButton({ active, onClick, icon: Icon, children }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={clsx(
        "flex items-center gap-1.5 border-b-2 px-3 py-2.5 text-fluid-sm font-medium transition-colors -mb-px",
        active ? "border-marigold text-ink" : "border-transparent text-ink-muted hover:text-ink"
      )}
    >
      <Icon className="h-4 w-4" aria-hidden="true" />
      {children}
    </button>
  );
}