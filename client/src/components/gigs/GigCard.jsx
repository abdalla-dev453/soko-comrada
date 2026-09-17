import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Star, Zap, TrendingUp, MapPin, MapPinned, Users, Clock, AlertOctagon } from "lucide-react";

import { formatCurrency } from "../../utils/formatCurrency";
import { pressable } from "../../utils/motion";

export function GigCard({ gig }) {
  const isDisputed = gig.status === "DISPUTED";
  const isPendingConfirmation = gig.status === "PENDING_CONFIRMATION";
  const isMultiSlot = gig.slots_needed > 1;

  return (
    <motion.div variants={pressable} initial="rest" whileHover="hover" whileTap="tap">
      <Link
        to={`/gigs/${gig.id}`}
        className="card block bg-surface-raised shadow-card hover:shadow-card-hover transition-shadow p-5 rounded-card focus-visible:outline-offset-4"
      >
        {/* Status banners for non-standard states — flat, no border. */}
        {isDisputed && (
          <div className="flex items-center gap-1.5 mb-2 text-xs font-medium text-danger">
            <AlertOctagon className="h-3.5 w-3.5" aria-hidden="true" />
            Under dispute — admin reviewing
          </div>
        )}
        {isPendingConfirmation && (
          <div className="flex items-center gap-1.5 mb-2 text-xs font-medium text-warning">
            <Clock className="h-3.5 w-3.5" aria-hidden="true" />
            Awaiting confirmation (48h window)
          </div>
        )}
        {gig.flagged_for_review && (
          <div className="flex items-center gap-1.5 mb-2 text-xs font-medium text-ink-muted">
            <Clock className="h-3.5 w-3.5" aria-hidden="true" />
            Under review — not yet visible on feed
          </div>
        )}

        <div className="flex items-start justify-between gap-3 mb-2">
          <h3 className="font-display font-semibold text-base leading-snug line-clamp-2">
            {gig.title}
          </h3>
          <span className="flex-shrink-0 font-display font-semibold text-base text-ink">
            {formatCurrency(gig.budget)}
          </span>
        </div>

        <p className="text-sm text-ink-muted line-clamp-2 mb-3">{gig.description}</p>

        <div className="flex flex-wrap items-center gap-x-3 gap-y-1.5 text-xs text-ink-muted">
          <span className="inline-flex items-center gap-1">
            <MapPin className="h-3.5 w-3.5" aria-hidden="true" />
            {gig.campus_location}
          </span>
          {gig.landmark && (
            <span className="inline-flex items-center gap-1 text-ink-muted">
              <MapPinned className="h-3.5 w-3.5" aria-hidden="true" />
              {gig.landmark}
            </span>
          )}
          <span className="rounded-full bg-ink/5 px-2 py-0.5">{gig.category}</span>
          {isMultiSlot && (
            <span className="inline-flex items-center gap-1 rounded-full bg-ink/5 px-2 py-0.5 font-medium">
              <Users className="h-3 w-3" aria-hidden="true" />
              {gig.slots_filled}/{gig.slots_needed} filled
            </span>
          )}
          {gig.is_urgent && (
            <span className="inline-flex items-center gap-1 rounded-full bg-warning-soft px-2 py-0.5 text-warning font-medium">
              <Zap className="h-3 w-3" aria-hidden="true" />
              Urgent
            </span>
          )}
          {gig.is_boosted && (
            <span className="inline-flex items-center gap-1 rounded-full bg-accent-soft px-2 py-0.5 text-accent font-medium">
              <TrendingUp className="h-3 w-3" aria-hidden="true" />
              Boosted
            </span>
          )}
        </div>

        {gig.poster && (
          <div className="mt-3 pt-3 flex items-center justify-between">
            <span className="text-xs text-ink-muted">{gig.poster.name}</span>
            {gig.poster.avg_rating != null && (
              <span className="inline-flex items-center gap-1 text-xs text-ink-muted">
                <Star className="h-3.5 w-3.5 fill-accent text-accent" aria-hidden="true" />
                {gig.poster.avg_rating.toFixed(1)}
              </span>
            )}
          </div>
        )}
      </Link>
    </motion.div>
  );
}