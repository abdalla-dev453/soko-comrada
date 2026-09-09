import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { motion } from "framer-motion";
import { MapPin, Zap, TrendingUp, Star, Flag, ShieldAlert } from "lucide-react";

import { SEO } from "../components/common/SEO";
import { Button } from "../components/common/Button";
import { Modal } from "../components/common/Modal";
import { SectionLoader } from "../components/common/Loader";
import { ErrorBanner, fieldClasses } from "../components/common/ErrorBanner";
import { StickyMobileCTA } from "../components/layout/StickyMobileCTA";
import { BoostModal } from "../components/payments/BoostModal";
import {
  applyToGig,
  completeGig,
  decideApplication,
  fetchGig,
  fetchGigApplications,
  submitReport,
  submitReview,
} from "../api/gigs";
import { formatCurrency } from "../utils/formatCurrency";
import { useAuth } from "../hooks/useAuth";
import { useToast } from "../hooks/useToast";

export default function GigDetail() {
  const { gigId } = useParams();
  const { user, isAuthenticated } = useAuth();
  const { toast } = useToast();

  const [gig, setGig] = useState(null);
  const [applications, setApplications] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState("");

  const [proposal, setProposal] = useState("");
  const [applying, setApplying] = useState(false);
  const [applyError, setApplyError] = useState("");
  const [applied, setApplied] = useState(false);

  const [completing, setCompleting] = useState(false);
  const [boostOpen, setBoostOpen] = useState(false);
  const [reviewOpen, setReviewOpen] = useState(false);
  const [reportOpen, setReportOpen] = useState(false);

  const isPoster = gig && user && gig.poster_id === user.id;

  const load = async () => {
    setLoading(true);
    setLoadError("");
    try {
      const gigData = await fetchGig(gigId);
      setGig(gigData);
      if (isAuthenticated && user && gigData.poster_id === user.id) {
        setApplications(await fetchGigApplications(gigId));
      }
    } catch (err) {
      setLoadError(err.message || "Couldn't load this gig.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [gigId, isAuthenticated]);

  const handleApply = async (e) => {
    e.preventDefault();
    setApplyError("");
    setApplying(true);
    try {
      await applyToGig(gigId, proposal.trim());
      setApplied(true);
      toast({
        variant: "success",
        title: "Application sent",
        description: "The poster will review it and get back to you.",
      });
    } catch (err) {
      setApplyError(err.message || "Couldn't send your application.");
    } finally {
      setApplying(false);
    }
  };

  const handleDecision = async (applicationId, status) => {
    try {
      await decideApplication(applicationId, status);
      toast({
        variant: "success",
        title: status === "ACCEPTED" ? "Applicant accepted" : "Applicant rejected",
      });
      await load();
    } catch (err) {
      toast({ variant: "error", title: "Couldn't update that application", description: err.message });
    }
  };

  const handleComplete = async () => {
    setCompleting(true);
    try {
      await completeGig(gigId);
      toast({
        variant: "success",
        title: "Gig marked complete",
        description: "Leave a review when you're ready.",
      });
      await load();
      setReviewOpen(true);
    } catch (err) {
      toast({ variant: "error", title: "Couldn't complete this gig", description: err.message });
    } finally {
      setCompleting(false);
    }
  };

  if (loading) return <SectionLoader label="Loading gig…" />;

  if (loadError || !gig) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-16 sm:px-6">
        <ErrorBanner title="Gig not found" message={loadError || "This gig may have been removed."} />
        <Link to="/gigs" className="mt-4 inline-block text-fluid-sm text-ink underline decoration-dotted">
          Back to all gigs
        </Link>
      </div>
    );
  }

  const acceptedApplication = applications?.find((a) => a.status === "ACCEPTED");
  const counterpartyId = isPoster ? acceptedApplication?.applicant.id : gig.poster_id;
  const canComplete =
    (gig.status === "IN_PROGRESS" || gig.status === "OPEN") &&
    isAuthenticated &&
    (isPoster || acceptedApplication?.applicant.id === user?.id);
  const canApply = gig.status === "OPEN" && isAuthenticated && !isPoster;

  return (
    <>
      <SEO title={gig.title} description={gig.description.slice(0, 155)} path={`/gigs/${gig.id}`} />

      <div className="mx-auto max-w-3xl px-4 py-10 sm:px-6">
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.35 }}>
          <div className="flex flex-wrap items-center gap-2 text-fluid-xs text-ink-muted mb-3">
            <span className="inline-flex items-center gap-1">
              <MapPin className="h-3.5 w-3.5" aria-hidden="true" />
              {gig.campus_location}
            </span>
            <span className="rounded-full bg-ink/5 px-2 py-0.5">{gig.category}</span>
            {gig.is_urgent && (
              <span className="inline-flex items-center gap-1 rounded-full bg-coral-soft px-2 py-0.5 text-coral-strong font-medium">
                <Zap className="h-3 w-3" aria-hidden="true" /> Urgent
              </span>
            )}
            {gig.is_boosted && (
              <span className="inline-flex items-center gap-1 rounded-full bg-marigold-soft px-2 py-0.5 text-marigold-strong font-medium">
                <TrendingUp className="h-3 w-3" aria-hidden="true" /> Boosted
              </span>
            )}
          </div>

          <div className="flex items-start justify-between gap-4">
            <h1 className="font-display font-semibold text-fluid-2xl">{gig.title}</h1>
            <span className="flex-shrink-0 font-display font-semibold text-fluid-xl">
              {formatCurrency(gig.budget)}
            </span>
          </div>

          {gig.poster && (
            <Link
              to={`/users/${gig.poster.id}`}
              className="mt-3 inline-flex items-center gap-2 text-fluid-sm text-ink-muted hover:text-ink"
            >
              Posted by <span className="text-ink font-medium">{gig.poster.name}</span>
              {gig.poster.avg_rating != null && (
                <span className="inline-flex items-center gap-1">
                  <Star className="h-3.5 w-3.5 fill-marigold text-marigold" aria-hidden="true" />
                  {gig.poster.avg_rating.toFixed(1)}
                </span>
              )}
            </Link>
          )}

          <p className="mt-6 text-fluid-base text-ink whitespace-pre-line leading-relaxed">
            {gig.description}
          </p>

          <div className="mt-8 flex flex-wrap gap-3">
            {isPoster && gig.status === "OPEN" && (
              <Button variant="secondary" onClick={() => setBoostOpen(true)}>
                Boost this gig
              </Button>
            )}
            {canComplete && (
              <Button loading={completing} onClick={handleComplete} className="hidden md:inline-flex">
                Mark as completed
              </Button>
            )}
            {gig.status === "COMPLETED" && isAuthenticated && (
              <Button variant="secondary" onClick={() => setReviewOpen(true)}>
                Leave a review
              </Button>
            )}
            {isAuthenticated && (
              <Button
                variant="ghost"
                icon={Flag}
                onClick={() => setReportOpen(true)}
                className="!text-ink-muted"
              >
                Report
              </Button>
            )}
          </div>

          {isPoster && applications && (
            <div className="mt-10 border-t border-border pt-8">
              <h2 className="font-display font-semibold text-fluid-lg mb-4">
                Applicants ({applications.length})
              </h2>
              {applications.length === 0 ? (
                <p className="text-fluid-sm text-ink-muted">No applications yet.</p>
              ) : (
                <ul className="flex flex-col gap-3">
                  {applications.map((app) => (
                    <li
                      key={app.id}
                      className="rounded-lg border border-border bg-surface p-4 flex items-start justify-between gap-4"
                    >
                      <div>
                        <p className="font-medium text-fluid-sm">
                          {app.applicant.name}{" "}
                          {app.applicant.avg_rating != null && (
                            <span className="inline-flex items-center gap-1 text-fluid-xs text-ink-muted ml-1">
                              <Star className="h-3 w-3 fill-marigold text-marigold" aria-hidden="true" />
                              {app.applicant.avg_rating.toFixed(1)}
                            </span>
                          )}
                        </p>
                        {app.proposal_text && (
                          <p className="mt-1 text-fluid-sm text-ink-muted">{app.proposal_text}</p>
                        )}
                        <p className="mt-1 text-fluid-xs text-ink-muted">Status: {app.status}</p>
                      </div>
                      {app.status === "PENDING" && (
                        <div className="flex flex-shrink-0 gap-2">
                          <Button size="sm" onClick={() => handleDecision(app.id, "ACCEPTED")}>
                            Accept
                          </Button>
                          <Button
                            size="sm"
                            variant="secondary"
                            onClick={() => handleDecision(app.id, "REJECTED")}
                          >
                            Reject
                          </Button>
                        </div>
                      )}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}

          {canApply && !applied && (
            <div className="mt-10 border-t border-border pt-8">
              <h2 className="font-display font-semibold text-fluid-lg mb-3">Apply for this gig</h2>
              <form onSubmit={handleApply} className="flex flex-col gap-3">
                {applyError && <ErrorBanner message={applyError} onDismiss={() => setApplyError("")} />}
                <div>
                  <label htmlFor="proposal" className="text-fluid-sm font-medium text-ink">
                    A short note to the poster (optional)
                  </label>
                  <textarea
                    id="proposal"
                    rows={3}
                    value={proposal}
                    onChange={(e) => setProposal(e.target.value)}
                    placeholder="I can start this afternoon and I've done similar work before…"
                    className={`${fieldClasses(false)} mt-1 resize-none`}
                  />
                </div>
                <Button type="submit" loading={applying} className="hidden md:inline-flex self-start">
                  Send application
                </Button>
              </form>
            </div>
          )}

          {applied && (
            <div className="mt-10 border-t border-border pt-8">
              <p className="text-fluid-sm text-moss-strong font-medium">
                Your application is in — the poster will reach out if you're picked.
              </p>
            </div>
          )}

          {!isAuthenticated && gig.status === "OPEN" && (
            <div className="mt-10 border-t border-border pt-8">
              <p className="text-fluid-sm text-ink-muted">
                <Link
                  to="/login"
                  state={{ from: `/gigs/${gig.id}` }}   
                  className="text-ink underline decoration-dotted"
                >
                  Log in
                </Link>{" "}
                to apply for this gig.
              </p>
            </div>  
          )}
        </motion.div>
      </div>

      <StickyMobileCTA show={canApply && !applied}>
        <Button onClick={handleApply} loading={applying} fullWidth>
          Send application
        </Button>
      </StickyMobileCTA>
      <StickyMobileCTA show={canComplete}>
        <Button loading={completing} onClick={handleComplete} fullWidth>
          Mark as completed
        </Button>
      </StickyMobileCTA>

      <BoostModal open={boostOpen} onClose={() => setBoostOpen(false)} gigId={gig.id} onSubmitted={load} />

      <ReviewModal
        open={reviewOpen}
        onClose={() => setReviewOpen(false)}
        gigId={gig.id}
        revieweeId={counterpartyId}
      />

      <ReportModal open={reportOpen} onClose={() => setReportOpen(false)} gigId={gig.id} />
    </>
  );
}

function ReviewModal({ open, onClose, gigId, revieweeId }) {
  const { toast } = useToast();
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!revieweeId) {
      setError("We couldn't tell who to review for this gig.");
      return;
    }
    setSubmitting(true);
    setError("");
    try {
      await submitReview({ gigId, revieweeId, rating, comment: comment.trim() || undefined });
      toast({ variant: "success", title: "Review posted" });
      setComment("");
      onClose();
    } catch (err) {
      setError(err.message || "Couldn't submit your review.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal open={open} onClose={onClose} title="Leave a review">
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        {error && <ErrorBanner message={error} onDismiss={() => setError("")} />}
        <div>
          <span className="text-fluid-sm font-medium text-ink">Rating</span>
          <div className="mt-2 flex gap-1">
            {[1, 2, 3, 4, 5].map((n) => (
              <button
                key={n}
                type="button"
                onClick={() => setRating(n)}
                aria-label={`${n} star${n > 1 ? "s" : ""}`}
                className="p-1"
              >
                <Star
                  className={`h-6 w-6 ${n <= rating ? "fill-marigold text-marigold" : "text-border"}`}
                  aria-hidden="true"
                />
              </button>
            ))}
          </div>
        </div>
        <div>
          <label htmlFor="review-comment" className="text-fluid-sm font-medium text-ink">
            Comment (optional)
          </label>
          <textarea
            id="review-comment"
            rows={3}
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            className={`${fieldClasses(false)} mt-1 resize-none`}
          />
        </div>
        <Button type="submit" loading={submitting} fullWidth>
          Post review
        </Button>
      </form>
    </Modal>
  );
}

function ReportModal({ open, onClose, gigId }) {
  const { toast } = useToast();
  const [reason, setReason] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (reason.trim().length < 3) {
      setError("Tell us a bit more about what happened.");
      return;
    }
    setSubmitting(true);
    setError("");
    try {
      await submitReport({ reason: reason.trim(), reportedGigId: gigId });
      toast({ variant: "success", title: "Report sent", description: "An admin will review it shortly." });
      setReason("");
      onClose();
    } catch (err) {
      setError(err.message || "Couldn't submit your report.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal open={open} onClose={onClose} title="Report this gig">
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div className="flex items-start gap-2 rounded-lg bg-coral-soft px-3 py-2.5 text-fluid-xs text-ink-muted">
          <ShieldAlert className="h-4 w-4 flex-shrink-0 text-coral-strong mt-0.5" aria-hidden="true" />
          Reports go straight to the admin queue — use this for scams, no-shows, or abuse.
        </div>
        {error && <ErrorBanner message={error} onDismiss={() => setError("")} />}
        <div>
          <label htmlFor="report-reason" className="text-fluid-sm font-medium text-ink">
            What happened?
          </label>
          <textarea
            id="report-reason"
            rows={3}
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            className={`${fieldClasses(Boolean(error))} mt-1 resize-none`}
          />
        </div>
        <Button type="submit" variant="danger" loading={submitting} fullWidth>
          Submit report
        </Button>
      </form>
    </Modal>
  );
}