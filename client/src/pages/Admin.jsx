import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Wallet, Flag, Check, X, Scale } from "lucide-react";
import clsx from "clsx";

import { SEO } from "../components/common/SEO";
import { Button } from "../components/common/Button";
import { EmptyState } from "../components/common/EmptyState";
import { SectionLoader } from "../components/common/Loader";
import {
  decidePayment,
  fetchDisputes,
  fetchPendingPayments,
  fetchReports,
  resolveDispute,
  resolveReport,
} from "../api/payments";
import { formatCurrency } from "../utils/formatCurrency";
import { useToast } from "../hooks/useToast";

export default function Admin() {
  const [tab, setTab] = useState("payments");
  const [payments, setPayments] = useState(null);
  const [reports, setReports] = useState(null);
  const [disputes, setDisputes] = useState(null);
  const { toast } = useToast();

  const loadPayments = () => fetchPendingPayments().then(setPayments).catch(() => setPayments([]));
  const loadReports = () => fetchReports("OPEN").then(setReports).catch(() => setReports([]));
  const loadDisputes = () => fetchDisputes().then(setDisputes).catch(() => setDisputes([]));

  useEffect(() => {
    loadPayments();
    loadReports();
    loadDisputes();
  }, []);

  const handlePaymentDecision = async (paymentId, approve) => {
    try {
      await decidePayment(paymentId, approve);
      toast({
        variant: "success",
        title: approve ? "Payment verified" : "Payment rejected",
      });
      loadPayments();
    } catch (err) {
      toast({ variant: "error", title: "Couldn't update that payment", description: err.message });
    }
  };

  const handleReportResolution = async (reportId, status) => {
    try {
      await resolveReport(reportId, status);
      toast({ variant: "success", title: status === "REVIEWED" ? "Marked reviewed" : "Dismissed" });
      loadReports();
    } catch (err) {
      toast({ variant: "error", title: "Couldn't update that report", description: err.message });
    }
  };

  const handleDisputeResolution = async (gigId, resolution) => {
    try {
      await resolveDispute(gigId, resolution);
      toast({
        variant: "success",
        title: resolution === "COMPLETED" ? "Resolved — marked completed" : "Resolved — gig cancelled",
      });
      loadDisputes();
    } catch (err) {
      toast({ variant: "error", title: "Couldn't resolve that dispute", description: err.message });
    }
  };

  return (
    <>
      <SEO title="Admin" description="Payment verification, reports, and disputes queue." path="/admin" noindex />

      <div className="mx-auto max-w-4xl px-4 py-10 sm:px-6">
        <h1 className="font-display font-semibold text-fluid-2xl mb-2">Admin</h1>
        <p className="text-fluid-sm text-ink-muted mb-8">
          Manual M-Pesa verification, trust &amp; safety reports, and dispute resolution.
        </p>

        <div className="flex gap-1 border-b border-border mb-6 overflow-x-auto scrollbar-none">
          <TabButton active={tab === "payments"} onClick={() => setTab("payments")} icon={Wallet}>
            Pending payments {payments && `(${payments.length})`}
          </TabButton>
          <TabButton active={tab === "reports"} onClick={() => setTab("reports")} icon={Flag}>
            Open reports {reports && `(${reports.length})`}
          </TabButton>
          <TabButton active={tab === "disputes"} onClick={() => setTab("disputes")} icon={Scale}>
            Disputes {disputes && `(${disputes.length})`}
          </TabButton>
        </div>

        {tab === "payments" && (
          <>
            {payments === null && <SectionLoader label="Loading pending payments…" />}
            {payments && payments.length === 0 && (
              <EmptyState icon={Wallet} title="Queue is clear" description="No payments waiting on verification." />
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
                        {p.purpose === "BOOST" ? "Gig boost" : "Entrepreneur subscription"} —{" "}
                        {formatCurrency(p.amount)}
                        {p.gig_id && (
                          <>
                            {" · "}
                            <Link to={`/gigs/${p.gig_id}`} className="underline decoration-dotted">
                              gig #{p.gig_id}
                            </Link>
                          </>
                        )}
                      </p>
                      <p className="mt-0.5 text-fluid-xs text-ink-muted">
                        code <span className="font-mono">{p.mpesa_code}</span> · submitted{" "}
                        {new Date(p.created_at).toLocaleString("en-KE", { dateStyle: "medium", timeStyle: "short" })}
                      </p>
                    </div>
                    <div className="flex flex-shrink-0 gap-2">
                      <Button size="sm" icon={Check} onClick={() => handlePaymentDecision(p.id, true)}>
                        Verify
                      </Button>
                      <Button
                        size="sm"
                        variant="danger"
                        icon={X}
                        onClick={() => handlePaymentDecision(p.id, false)}
                      >
                        Reject
                      </Button>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </>
        )}

        {tab === "reports" && (
          <>
            {reports === null && <SectionLoader label="Loading reports…" />}
            {reports && reports.length === 0 && (
              <EmptyState icon={Flag} title="No open reports" description="Nothing flagged for review right now." />
            )}
            {reports && reports.length > 0 && (
              <ul className="flex flex-col gap-3">
                {reports.map((r) => (
                  <li
                    key={r.id}
                    className="flex items-start justify-between gap-4 rounded-lg border border-border bg-surface p-4"
                  >
                    <div>
                      <p className="text-fluid-sm text-ink">{r.reason}</p>
                      <p className="mt-1 text-fluid-xs text-ink-muted flex flex-wrap gap-x-3">
                        {r.reported_gig_id && (
                          <Link to={`/gigs/${r.reported_gig_id}`} className="underline decoration-dotted">
                            gig #{r.reported_gig_id}
                          </Link>
                        )}
                        {r.reported_user_id && (
                          <Link to={`/users/${r.reported_user_id}`} className="underline decoration-dotted">
                            user #{r.reported_user_id}
                          </Link>
                        )}
                        <span>
                          {new Date(r.created_at).toLocaleString("en-KE", { dateStyle: "medium", timeStyle: "short" })}
                        </span>
                      </p>
                    </div>
                    <div className="flex flex-shrink-0 gap-2">
                      <Button size="sm" onClick={() => handleReportResolution(r.id, "REVIEWED")}>
                        Mark reviewed
                      </Button>
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={() => handleReportResolution(r.id, "DISMISSED")}
                      >
                        Dismiss
                      </Button>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </>
        )}

        {tab === "disputes" && (
          <>
            {disputes === null && <SectionLoader label="Loading disputes…" />}
            {disputes && disputes.length === 0 && (
              <EmptyState
                icon={Scale}
                title="No open disputes"
                description="Disputed gigs appear here when a completion is contested."
              />
            )}
            {disputes && disputes.length > 0 && (
              <ul className="flex flex-col gap-3">
                {disputes.map((gig) => (
                  <li
                    key={gig.id}
                    className="flex items-start justify-between gap-4 rounded-lg border border-coral/30 bg-coral-soft/30 p-4"
                  >
                    <div>
                      <p className="font-medium text-fluid-sm text-ink">{gig.title}</p>
                      <Link
                        to={`/gigs/${gig.id}`}
                        className="text-fluid-xs text-ink underline decoration-dotted"
                      >
                        View gig #{gig.id}
                      </Link>
                      {gig.dispute_reason && (
                        <p className="mt-1.5 text-fluid-xs text-ink-muted italic">
                          "{gig.dispute_reason}"
                        </p>
                      )}
                    </div>
                    <div className="flex flex-shrink-0 gap-2">
                      <Button size="sm" onClick={() => handleDisputeResolution(gig.id, "COMPLETED")}>
                        Mark completed
                      </Button>
                      <Button
                        size="sm"
                        variant="danger"
                        onClick={() => handleDisputeResolution(gig.id, "CANCELLED")}
                      >
                        Cancel gig
                      </Button>
                    </div>
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