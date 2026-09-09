import { AnimatePresence, motion } from "framer-motion";

/**
 * A page can drop this in when it has one primary action that should
 * stay reachable while scrolling on a phone (e.g. "Apply to this
 * gig" on the gig detail page). It sits just above the BottomTabBar,
 * not instead of it, and only renders on mobile — desktop already
 * shows the action inline.
 */
export function StickyMobileCTA({ show = true, children }) {
  return (
    <AnimatePresence>
      {show && (
        <motion.div
          initial={{ y: 80, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: 80, opacity: 0 }}
          transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
          className="fixed inset-x-0 bottom-[calc(4rem+env(safe-area-inset-bottom))] z-30 px-4 pb-3 pt-2 md:hidden"
        >
          <div className="mx-auto max-w-md rounded-xl bg-surface-raised shadow-popover border border-border p-3">
            {children}
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}