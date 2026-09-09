import { Link, useLocation } from "react-router-dom";
import { motion } from "framer-motion";
import { CheckCircle2 } from "lucide-react";

import { SEO } from "../components/common/SEO";
import { Button } from "../components/common/Button";

const COPY = {
  contact: {
    title: "Message on its way",
    body: "Thanks for reaching out — we typically reply within a day or two.",
  },
  gig: {
    title: "Your gig is live",
    body: "It's on the feed for your campus now. We'll notify you as applications come in.",
  },
  default: {
    title: "All set",
    body: "That went through successfully.",
  },
};

export default function ThankYou() {
  const location = useLocation();
  const { context, title: gigTitle } = location.state || {};
  const resolvedContext = context || (gigTitle ? "gig" : "default");
  const copy = COPY[resolvedContext] || COPY.default;

  return (
    <>
      <SEO title="Thank you" description="Confirmation page." path="/thank-you" noindex />
      <div className="mx-auto flex min-h-[70vh] max-w-md flex-col items-center justify-center px-4 py-16 text-center sm:px-6">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
        >
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-moss-soft text-moss-strong mb-5">
            <CheckCircle2 className="h-7 w-7" aria-hidden="true" />
          </div>
          <h1 className="font-display font-semibold text-fluid-2xl">{copy.title}</h1>
          <p className="mt-3 text-fluid-sm text-ink-muted">
            {gigTitle ? `"${gigTitle}" is posted. ${copy.body}` : copy.body}
          </p>
          <div className="mt-8 flex flex-wrap justify-center gap-3">
            <Button as={Link} to="/gigs">
              Browse gigs
            </Button>
            <Button as={Link} to="/" variant="secondary">
              Back home
            </Button>
          </div>
        </motion.div>
      </div>
    </>
  );
}