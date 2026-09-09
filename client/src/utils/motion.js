/**
 * A small, deliberate set of motion variants. Per the design brief:
 * one orchestrated reveal on first load, plus micro-interactions that
 * respond to a person's action — not scroll-triggered fades scattered
 * across every section.
 */

export const heroContainer = {
  hidden: {},
  show: {
    transition: {
      staggerChildren: 0.09,
      delayChildren: 0.05,
    },
  },
};

export const heroItem = {
  hidden: { opacity: 0, y: 16 },
  show: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.6, ease: [0.16, 1, 0.3, 1] },
  },
};

/** Tap/hover feedback for interactive controls — buttons, ticket cards. */
export const pressable = {
  rest: { scale: 1 },
  hover: { scale: 1.015, transition: { duration: 0.18, ease: "easeOut" } },
  tap: { scale: 0.985, transition: { duration: 0.1 } },
};

/** Drawer / sheet slide-in (mobile nav, filters). */
export const slideUpSheet = {
  hidden: { y: "100%", opacity: 0.4 },
  show: { y: 0, opacity: 1, transition: { duration: 0.32, ease: [0.16, 1, 0.3, 1] } },
  exit: { y: "100%", opacity: 0.4, transition: { duration: 0.22, ease: "easeIn" } },
};

/** Side drawer (mobile nav menu). */
export const slideInPanel = {
  hidden: { x: "100%" },
  show: { x: 0, transition: { duration: 0.28, ease: [0.16, 1, 0.3, 1] } },
  exit: { x: "100%", transition: { duration: 0.22, ease: "easeIn" } },
};

export const fadeScale = {
  hidden: { opacity: 0, scale: 0.97 },
  show: { opacity: 1, scale: 1, transition: { duration: 0.22, ease: "easeOut" } },
  exit: { opacity: 0, scale: 0.98, transition: { duration: 0.15, ease: "easeIn" } },
};

export const toastSlide = {
  hidden: { opacity: 0, y: 12, scale: 0.98 },
  show: { opacity: 1, y: 0, scale: 1, transition: { duration: 0.25, ease: [0.16, 1, 0.3, 1] } },
  exit: { opacity: 0, y: 8, scale: 0.98, transition: { duration: 0.15 } },
};