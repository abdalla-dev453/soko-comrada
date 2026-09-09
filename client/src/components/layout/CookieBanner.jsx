import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Link } from "react-router-dom";

import { Button } from "../common/Button";

const STORAGE_KEY = "soko_comrada_cookie_consent"; // "accepted" | "declined"

export function CookieBanner() {
  const [choice, setChoice] = useState(null);

  useEffect(() => {
    setChoice(localStorage.getItem(STORAGE_KEY));
  }, []);

  const decide = (value) => {
    localStorage.setItem(STORAGE_KEY, value);
    setChoice(value);
  };

  const visible = choice === null;

  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          initial={{ y: 80, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: 80, opacity: 0 }}
          transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
          role="region"
          aria-label="Cookie notice"
          className="fixed inset-x-0 bottom-16 z-50 px-4 pb-3 md:bottom-4"
        >
          <div className="mx-auto flex max-w-2xl flex-col gap-3 rounded-xl border border-border bg-surface-raised p-4 shadow-popover sm:flex-row sm:items-center sm:justify-between">
            <p className="text-fluid-sm text-ink-muted">
              We use a small set of cookies to keep you signed in and understand which
              features people actually use. See our{" "}
              <Link to="/privacy" className="text-ink underline decoration-dotted">
                privacy policy
              </Link>
              .
            </p>
            <div className="flex gap-2 flex-shrink-0">
              <Button variant="secondary" size="sm" onClick={() => decide("declined")}>
                Decline
              </Button>
              <Button size="sm" onClick={() => decide("accepted")}>
                Accept
              </Button>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}