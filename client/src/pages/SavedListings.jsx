import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Star, Trash2, Zap } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

import { SEO } from "../components/common/SEO";
import { Button } from "../components/common/Button";
import { EmptyState } from "../components/common/EmptyState";
import { SectionLoader } from "../components/common/Loader";
import { fetchSavedListings, unsaveListing } from "../api/gigs";
import { useToast } from "../hooks/useToast";

export default function SavedListings() {
  const { toast } = useToast();
  const [saved, setSaved] = useState(null);

  useEffect(() => {
    fetchSavedListings()
      .then(setSaved)
      .catch(() => setSaved([]));
  }, []);

  const handleUnsave = async (gigId) => {
    try {
      await unsaveListing(gigId);
      setSaved((prev) => (prev || []).filter((g) => g.id !== gigId));
      toast({ title: "Removed", description: "Listing removed from saved." });
    } catch (err) {
      toast({ variant: "error", title: "Couldn't remove listing", description: err.message });
    }
  };

  return (
    <>
      <SEO
        title="Saved listings"
        description="Your bookmarked gigs and services."
        path="/saved"
        noindex
      />

      <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6">
        <h1 className="font-display font-semibold text-fluid-2xl mb-2">Saved</h1>
        <p className="text-fluid-sm text-ink-muted mb-8">
          Your bookmarked gigs, services, and marketplace items.
        </p>

        {saved === null && <SectionLoader label="Loading saved listings…" />}

        {saved && saved.length === 0 && (
          <EmptyState
            icon={Star}
            title="Nothing saved yet"
            description="Star a gig to keep it for later."
            action={
              <Button as={Link} to="/gigs">
                Browse gigs
              </Button>
            }
          />
        )}

        {saved && saved.length > 0 && (
          <AnimatePresence>
            <motion.ul
              className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3"
              initial="hidden"
              animate="show"
              variants={{
                show: { transition: { staggerChildren: 0.06 } },
              }}
            >
              {saved.map((gig) => (
                <motion.li key={gig.id} variants={{ show: { opacity: 1, y: 0 } }}>
                  <div className="ticket bg-surface shadow-card pl-6 pr-4 py-4 rounded-ticket">
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <h3 className="font-display font-semibold text-fluid-base line-clamp-2">
                        <Link
                          to={`/gigs/${gig.id}`}
                          className="hover:text-marigold transition-colors"
                        >
                          {gig.title}
                        </Link>
                      </h3>
                      <Button
                        size="sm"
                        variant="ghost"
                        icon={Trash2}
                        onClick={() => handleUnsave(gig.id)}
                        className="!text-ink-muted"
                        aria-label={`Remove ${gig.title} from saved`}
                      />
                    </div>
                    <p className="text-fluid-sm text-ink-muted line-clamp-2 mb-3">
                      {gig.description}
                    </p>
                    <div className="flex items-center justify-between">
                      <span className="font-display font-semibold text-fluid-base">
                        {gig.budget ? `KES ${gig.budget}` : "Negotiable"}
                      </span>
                      {gig.is_urgent && (
                        <span className="inline-flex items-center gap-1 rounded-full bg-coral-soft px-2 py-0.5 text-fluid-xs font-medium text-coral-strong">
                          <Zap className="h-3 w-3" /> Urgent
                        </span>
                      )}
                    </div>
                  </div>
                </motion.li>
              ))}
            </motion.ul>
          </AnimatePresence>
        )}
      </div>
    </>
  );
}
