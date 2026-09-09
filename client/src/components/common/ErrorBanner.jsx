import { AlertTriangle } from "lucide-react";
import { motion } from "framer-motion";

export function ErrorBanner({ title = "That didn't work", message, onDismiss }) {
  if (!message) return null;
  return (
    <motion.div
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: "auto" }}
      exit={{ opacity: 0, height: 0 }}
      role="alert"
      className="flex items-start gap-3 rounded-lg border border-coral/30 bg-coral-soft px-4 py-3 text-ink"
    >
      <AlertTriangle className="h-5 w-5 flex-shrink-0 text-coral-strong mt-0.5" aria-hidden="true" />
      <div className="flex-1 text-fluid-sm">
        <p className="font-medium">{title}</p>
        <p className="text-ink-muted">{message}</p>
      </div>
      {onDismiss && (
        <button
          type="button"
          onClick={onDismiss}
          className="text-ink-muted hover:text-ink text-fluid-sm underline decoration-dotted"
        >
          Dismiss
        </button>
      )}
    </motion.div>
  );
}

export function FieldError({ message }) {
  if (!message) return null;
  return (
    <p role="alert" className="mt-1 text-fluid-xs text-coral-strong">
      {message}
    </p>
  );
}

/** Wraps a form field, adding the coral border+ring treatment when
 * `error` is set — used by inputs across the auth/gig-creation forms. */
export function fieldClasses(hasError) {
  return [
    "w-full rounded-lg border bg-surface px-3.5 py-2.5 text-fluid-base text-ink placeholder:text-ink-muted",
    "transition-colors focus:outline-none focus:ring-2 focus:ring-offset-0",
    hasError
      ? "border-coral focus:ring-coral/40"
      : "border-border focus:border-moss focus:ring-moss/30",
  ].join(" ");
}