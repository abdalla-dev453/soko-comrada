import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Star, Briefcase, ClipboardList, Wallet, PlusCircle, ShieldCheck, Gift, Copy } from "lucide-react";
import clsx from "clsx";

import { SEO } from "../components/common/SEO";
import { Button } from "../components/common/Button";
import { EmptyState } from "../components/common/EmptyState";
import { SectionLoader } from "../components/common/Loader";
import { GigCard } from "../components/gigs/GigCard";
import { StatusBadge } from "../components/payments/SatausBadge";
import { PaymentModal } from "../components/payments/PaymentModal";
import { fetchMyApplications, fetchMyGigs } from "../api/gigs";
import { fetchMyPayments } from "../api/payments";
import { formatCurrency } from "../utils/formatCurrency";
import { useAuth } from "../hooks/useAuth";
import { useToast } from "../hooks/useToast";

export default function Dashboard() {
  const { user, refreshProfile } = useAuth();
  const { toast } = useToast();
  const [tab, setTab] = useState("gigs");
  const [gigs, setGigs] = useState(null);
  const [applications, setApplications] = useState(null);
  const [payments, setPayments] = useState(null);
  const [subscriptionOpen, setSubscriptionOpen] = useState(false);

  const loadPayments = () => fetchMyPayments().then(setPayments).catch(() => setPayments([]));

  useEffect(() => {
    fetchMyGigs().then(setGigs).catch(() => setGigs([]));
    fetchMyApplications().then(setApplications).catch(() => setApplications([]));
    loadPayments();
  }, []);

  return (
    <>
      <SEO title="Dashboard" description="Your posted gigs, applications, and payments on Soko Comrada." path="/dashboard" noindex />

      <div className="mx-auto max-w-5xl px-4 py-10 sm:px-6">
        <div className="mb-8 flex flex-wrap items-end justify-between gap-4">
          <div>
            <h1 className="font-display font-semibold text-fluid-2xl">
              Hi, {user?.name?.split(" ")[0]}
            </h1>
            <p className="mt-1 text-fluid-sm text-ink-muted flex flex-wrap items-center gap-3">
              {user?.campus_location}
              {user?.avg_rating != null && (
                <span className="inline-flex items-center gap-1">
                  <Star className="h-3.5 w-3.5 fill-marigold text-marigold" aria-hidden="true" />
                  {user.avg_rating.toFixed(1)}
                </span>
              )}
              {user?.is_verified_entrepreneur && (
                <span className="inline-flex items-center gap-1 rounded-full bg-marigold-soft px-2 py-0.5 text-fluid-xs font-medium text-marigold-strong">
                  <ShieldCheck className="h-3 w-3" aria-hidden="true" />
                  Verified entrepreneur
                </span>
              )}
            </p>
            {/* Referral code + credit count */}
            {user?.referral_code && (
              <div className="mt-3 flex items-center gap-3 rounded-lg border border-border bg-surface px-4 py-2.5 text-fluid-sm w-fit">
                <Gift className="h-4 w-4 flex-shrink-0 text-moss-strong" aria-hidden="true" />
                <span className="text-ink-muted">Referral code:</span>
                <span className="font-mono font-medium text-ink tracking-wider">{user.referral_code}</span>
                <button
                  type="button"
                  onClick={() => {
                    navigator.clipboard?.writeText(user.referral_code);
                    toast({ title: "Copied", description: "Share it with classmates — each one who joins earns you credit toward a free boost." });
                  }}
                  aria-label="Copy referral code"
                  className="text-ink-muted hover:text-ink"
                >
                  <Copy className="h-3.5 w-3.5" aria-hidden="true" />
                </button>
                {user.free_boost_credits > 0 && (
                  <span className="rounded-full bg-marigold-soft px-2 py-0.5 text-fluid-xs font-medium text-marigold-strong">
                    {user.free_boost_credits} free boost{user.free_boost_credits > 1 ? "s" : ""}
                  </span>
                )}
              </div>
            )}
          </div>
          <div className="flex flex-wrap gap-2">
            {!user?.is_verified_entrepreneur && (
              <Button variant="secondary" icon={ShieldCheck} onClick={() => setSubscriptionOpen(true)}>
                Get verified
              </Button>
            )}
            <Button as={Link} to="/gigs/new" icon={PlusCircle}>
              Post a gig
            </Button>
          </div>
        </div>

        <div className="flex gap-1 border-b border-border mb-6 overflow-x-auto scrollbar-none">
          <TabButton active={tab === "gigs"} onClick={() => setTab("gigs")} icon={Briefcase}>
            My gigs {gigs && `(${gigs.length})`}
          </TabButton>
          <TabButton active={tab === "applications"} onClick={() => setTab("applications")} icon={ClipboardList}>
            My applications {applications && `(${applications.length})`}
          </TabButton>
          <TabButton active={tab === "payments"} onClick={() => setTab("payments")} icon={Wallet}>
            Payments {payments && `(${payments.length})`}
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
                    <StatusBadge status={app.status} />
                  </li>
                ))}
              </ul>
            )}
          </>
        )}

        {tab === "payments" && (
          <>
            {payments === null && <SectionLoader label="Loading your payments…" />}
            {payments && payments.length === 0 && (
              <EmptyState
                icon={Wallet}
                title="No payments yet"
                description="Boost a gig or go for the verified-entrepreneur badge and your M-Pesa submissions will show up here."
              />
            )}
            {payments && payments.length > 0 && (
              <ul className="flex flex-col gap-3">
                {payments.map((p) => (
                  <li
                    key={p.id}
                    className="flex items-center justify-between gap-4 rounded-lg border border-border bg-surface p-4"
                  >
                    <div>
                      <p className="font-medium text-fluid-sm text-ink">
                        {p.purpose === "BOOST" ? "Gig boost" : p.purpose === "SUBSCRIPTION" ? "Entrepreneur subscription" : p.purpose}
                        {p.gig_id && (
                          <>
                            {" — "}
                            <Link to={`/gigs/${p.gig_id}`} className="underline decoration-dotted">
                              view gig
                            </Link>
                          </>
                        )}
                      </p>
                      <p className="mt-0.5 text-fluid-xs text-ink-muted">
                        {formatCurrency(p.amount)} · code {p.mpesa_code} ·{" "}
                        {new Date(p.created_at).toLocaleDateString("en-KE", { dateStyle: "medium" })}
                      </p>
                    </div>
                    <StatusBadge status={p.status} />
                  </li>
                ))}
              </ul>
            )}
          </>
        )}
      </div>

      <PaymentModal
        open={subscriptionOpen}
        onClose={() => setSubscriptionOpen(false)}
        purpose="SUBSCRIPTION"
        onSuccess={() => {
          loadPayments();
          refreshProfile();
        }}
      />
    </>
  );
}

function TabButton({ active, onClick, icon: Icon, children }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={clsx(
        "flex items-center gap-1.5 whitespace-nowrap border-b-2 px-3 py-2.5 text-fluid-sm font-medium transition-colors -mb-px",
        active ? "border-marigold text-ink" : "border-transparent text-ink-muted hover:text-ink"
      )}
    >
      <Icon className="h-4 w-4" aria-hidden="true" />
      {children}
    </button>
  );
}
