import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Home, Search } from "lucide-react";

import { SEO } from "../components/common/SEO";
import { Button } from "../components/common/Button";
import { heroContainer, heroItem } from "../utils/motion";

export default function NotFound() {
  return (
    <>
      <SEO
        title="Page not found"
        description="This page doesn't exist on Soko Comrada."
        path="/404"
        noindex
      />
      <div className="mx-auto flex min-h-[70vh] max-w-md flex-col items-center justify-center px-4 py-16 text-center sm:px-6">
        <motion.div variants={heroContainer} initial="hidden" animate="show">
          <motion.div variants={heroItem} className="mx-auto mb-6 w-40">
            <motion.svg
              viewBox="0 0 200 110"
              animate={{ rotate: [-2, 2, -2] }}
              transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
              role="img"
              aria-label="A torn ticket stub"
            >
              <rect x="4" y="4" width="192" height="102" rx="10" className="fill-surface stroke-border" strokeWidth="2" />
              <line x1="70" y1="10" x2="70" y2="100" strokeDasharray="6 6" className="stroke-border" strokeWidth="2" />
              <circle cx="70" cy="4" r="7" className="fill-bg" />
              <circle cx="70" cy="106" r="7" className="fill-bg" />
              <text x="37" y="63" textAnchor="middle" className="fill-ink" fontFamily="'Space Grotesk', sans-serif" fontWeight="700" fontSize="30">
                404
              </text>
              <text x="135" y="50" textAnchor="middle" className="fill-ink-muted" fontFamily="'Work Sans', sans-serif" fontSize="12">
                GIG
              </text>
              <text x="135" y="66" textAnchor="middle" className="fill-ink-muted" fontFamily="'Work Sans', sans-serif" fontSize="12">
                NOT FOUND
              </text>
            </motion.svg>
          </motion.div>

          <motion.h1 variants={heroItem} className="font-display font-semibold text-fluid-2xl">
            This one skipped town.
          </motion.h1>
          <motion.p variants={heroItem} className="mt-3 text-fluid-sm text-ink-muted">
            The gig or page you're after was taken, expired, or never existed. Let's get
            you back to something real.
          </motion.p>
          <motion.div variants={heroItem} className="mt-8 flex flex-wrap justify-center gap-3">
            <Button as={Link} to="/" icon={Home}>
              Back home
            </Button>
            <Button as={Link} to="/gigs" variant="secondary" icon={Search}>
              Browse gigs
            </Button>
          </motion.div>
        </motion.div>
      </div>
    </>
  );
}