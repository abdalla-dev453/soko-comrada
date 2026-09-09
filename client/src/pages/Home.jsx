import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowRight, ShieldCheck, Clock, MapPinned, Star } from "lucide-react";

import { SEO } from "../components/common/SEO";
import { Button } from "../components/common/Button";
import { GigCard } from "../components/gigs/GigCard";
import { GigFeedSkeleton } from "../components/common/Skeleton";
import { fetchGigs } from "../api/gigs";
import { useAuth } from "../hooks/useAuth";
import { trackCtaClick } from "../utils/analytics";
import { heroContainer, heroItem } from "../utils/motion";

const STEPS = [
  {
    number: "01",
    title: "Post what you need",
    description:
      "Formatting help, a haircut, moving boxes across campus — describe it, set a budget, flag it urgent if it can't wait.",
  },
  {
    number: "02",
    title: "Pick who does it",
    description:
      "Applicants from your own campus apply with a short note. Check their rating, pick one, and you're both locked in.",
  },
  {
    number: "03",
    title: "Get it done, rate it",
    description:
      "Either of you marks it complete, then you rate each other. That rating follows them to their next gig.",
  },
];

export default function Home() {
  const { isAuthenticated } = useAuth();
  const [gigs, setGigs] = useState(null);

  useEffect(() => {
    let cancelled = false;
    fetchGigs({}, 1)
      .then((data) => {
        if (!cancelled) setGigs(data.gigs.slice(0, 3));
      })
      .catch(() => {
        if (!cancelled) setGigs([]);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <>
      <SEO
        title="Soko Comrada — Campus gigs & hustles, sorted"
        description="Post a task or offer a skill on your campus. Fast, local, and verified by .ac.ke email — no more scrolling five WhatsApp groups."
        path="/"
      />

      <section className="mx-auto max-w-6xl px-4 pt-14 pb-16 sm:px-6 sm:pt-20 sm:pb-24">
        <motion.div variants={heroContainer} initial="hidden" animate="show" className="max-w-3xl">
          <motion.p variants={heroItem} className="mb-4 text-fluid-sm font-medium text-marigold-strong dark:text-marigold">
            Built for one campus at a time — starting with MUT- MURANG'A
          </motion.p>
          <motion.h1
            variants={heroItem}
            className="font-display font-semibold text-fluid-hero tracking-tight text-ink"
          >
            The hustle economy your campus already runs, minus the scams.
          </motion.h1>
          <motion.p variants={heroItem} className="mt-6 text-fluid-lg text-ink-muted max-w-2xl">
            ComradePLug turns your class group chats' informal gig economy into a real
            marketplace: verified students, visible ratings, and a fair price — all
            scoped to your own campus.
          </motion.p>
          <motion.div variants={heroItem} className="mt-8 flex flex-wrap items-center gap-3">
            <Button
              size="lg"
              icon={ArrowRight}
              iconPosition="right"
              onClick={() => trackCtaClick("hero_post_gig")}
              as={Link}
              to={isAuthenticated ? "/gigs/new" : "/register"}
            >
              Post a gig
            </Button>
            <Button
              size="lg"
              variant="secondary"
              onClick={() => trackCtaClick("hero_browse_gigs")}
              as={Link}
              to="/gigs"
            >
              Browse gigs
            </Button>
          </motion.div>
        </motion.div>
      </section>

      <section className="border-y border-border bg-surface">
        <div className="mx-auto max-w-6xl px-4 py-14 sm:px-6">
          <h2 className="font-display font-semibold text-fluid-2xl mb-10 max-w-xl">
            Three steps, no group chat required
          </h2>
          <div className="grid gap-8 sm:grid-cols-3">
            {STEPS.map((step) => (
              <div key={step.number}>
                <span className="font-display text-fluid-2xl text-marigold-strong">
                  {step.number}
                </span>
                <h3 className="mt-2 font-display font-semibold text-fluid-lg">{step.title}</h3>
                <p className="mt-2 text-fluid-sm text-ink-muted">{step.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-4 py-16 sm:px-6">
        <div className="flex items-end justify-between gap-4 mb-8">
          <h2 className="font-display font-semibold text-fluid-2xl">Open on campus right now</h2>
          <Link
            to="/gigs"
            className="hidden sm:inline-flex items-center gap-1 text-fluid-sm font-medium text-ink-muted hover:text-ink transition-colors"
          >
            View all <ArrowRight className="h-4 w-4" aria-hidden="true" />
          </Link>
        </div>

        {gigs === null && <GigFeedSkeleton count={3} />}
        {gigs && gigs.length === 0 && (
          <p className="text-fluid-sm text-ink-muted">
            No open gigs yet on the pilot campus —{" "}
            <Link to="/gigs/new" className="text-ink underline decoration-dotted">
              be the first to post one
            </Link>
            .
          </p>
        )}
        {gigs && gigs.length > 0 && (
          <div className="grid gap-4 sm:grid-cols-3">
            {gigs.map((gig) => (
              <GigCard key={gig.id} gig={gig} />
            ))}
          </div>
        )}
      </section>

      <section className="border-t border-border bg-ink text-surface">
        <div className="mx-auto max-w-6xl px-4 py-16 sm:px-6">
          <div className="grid gap-8 sm:grid-cols-3">
            <div className="flex gap-3">
              <ShieldCheck className="h-6 w-6 flex-shrink-0 text-marigold" aria-hidden="true" />
              <div>
                <h3 className="font-display font-semibold text-fluid-base">
                  Verified by student email
                </h3>
                <p className="mt-1 text-fluid-sm text-surface/70">
                  Registration is restricted to recognized .ac.ke domains, so you know
                  who you're dealing with.
                </p>
              </div>
            </div>
            <div className="flex gap-3">
              <MapPinned className="h-6 w-6 flex-shrink-0 text-marigold" aria-hidden="true" />
              <div>
                <h3 className="font-display font-semibold text-fluid-base">
                  Scoped to your campus
                </h3>
                <p className="mt-1 text-fluid-sm text-surface/70">
                  You're not competing with the whole city — just the people you'll
                  actually run into.
                </p>
              </div>
            </div>
            <div className="flex gap-3">
              <Clock className="h-6 w-6 flex-shrink-0 text-marigold" aria-hidden="true" />
              <div>
                <h3 className="font-display font-semibold text-fluid-base">
                  Built for "I need this in 2 hours"
                </h3>
                <p className="mt-1 text-fluid-sm text-surface/70">
                  Flag a gig urgent and it stands out in the feed — no channel for this
                  existed before.
                </p>
              </div>
            </div>
          </div>

          <div className="mt-14 flex flex-col items-start gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-center gap-1.5">
              {[...Array(5)].map((_, i) => (
                <Star key={i} className="h-4 w-4 fill-marigold text-marigold" aria-hidden="true" />
              ))}
              <span className="ml-2 text-fluid-sm text-surface/70">
                Rated by students who've actually used it
              </span>
            </div>
            <Button
              variant="secondary"
              className="!border-surface/30 !text-surface hover:!bg-surface/10"
              as={Link}
              to={isAuthenticated ? "/gigs/new" : "/register"}
            >
              Get started
            </Button>
          </div>
        </div>
      </section>
    </>
  );
}
