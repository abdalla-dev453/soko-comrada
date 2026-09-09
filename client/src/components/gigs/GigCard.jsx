import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Star, Zap, TrendingUp, MapPin } from "lucide-react";

import { formatCurrency } from "../../utils/formatCurrency";
import { pressable } from "../../utils/motion";

const SPINE_BY_STATE = {
  boosted: "#E8A33D", // marigold
  urgent: "#E8572F", // coral
  open: "#4C7A5D", // moss
};

export function GigCard({ gig }) {
  const state = gig.is_boosted ? "boosted" : gig.is_urgent ? "urgent" : "open";
  const spine = SPINE_BY_STATE[state];

  return (
    <motion.div variants={pressable} initial="rest" whileHover="hover" whileTap="tap">
      <Link
        to={`/gigs/${gig.id}`}
        className="ticket block bg-surface shadow-card hover:shadow-card-hover transition-shadow pl-6 pr-4 py-4 rounded-ticket focus-visible:outline-offset-4"
        style={{ "--spine": spine }}
      >
        <div className="flex items-start justify-between gap-3 mb-2">
          <h3 className="font-display font-semibold text-fluid-base leading-snug line-clamp-2">
            {gig.title}
          </h3>
          <span className="flex-shrink-0 font-display font-semibold text-fluid-base text-ink">
            {formatCurrency(gig.budget)}
          </span>
        </div>

        <p className="text-fluid-sm text-ink-muted line-clamp-2 mb-3">{gig.description}</p>

        <div className="flex flex-wrap items-center gap-x-3 gap-y-1.5 text-fluid-xs text-ink-muted">
          <span className="inline-flex items-center gap-1">
            <MapPin className="h-3.5 w-3.5" aria-hidden="true" />
            {gig.campus_location}
          </span>
          <span className="rounded-full bg-ink/5 px-2 py-0.5">{gig.category}</span>
          {gig.is_urgent && (
            <span className="inline-flex items-center gap-1 rounded-full bg-coral-soft px-2 py-0.5 text-coral-strong font-medium">
              <Zap className="h-3 w-3" aria-hidden="true" />
              Urgent
            </span>
          )}
          {gig.is_boosted && (
            <span className="inline-flex items-center gap-1 rounded-full bg-marigold-soft px-2 py-0.5 text-marigold-strong font-medium">
              <TrendingUp className="h-3 w-3" aria-hidden="true" />
              Boosted
            </span>
          )}
        </div>

        {gig.poster && (
          <div className="mt-3 pt-3 border-t border-border flex items-center justify-between">
            <span className="text-fluid-xs text-ink-muted">{gig.poster.name}</span>
            {gig.poster.avg_rating != null && (
              <span className="inline-flex items-center gap-1 text-fluid-xs text-ink-muted">
                <Star className="h-3.5 w-3.5 fill-marigold text-marigold" aria-hidden="true" />
                {gig.poster.avg_rating.toFixed(1)}
              </span>
            )}
          </div>
        )}
      </Link>
    </motion.div>
  );
}