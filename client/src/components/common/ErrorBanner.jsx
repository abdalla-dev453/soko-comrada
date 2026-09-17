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
      className="flex items-start gap-3 rounded-lg bg-danger-soft px-4 py-3 text-ink"
    >
      <AlertTriangle className="h-5 w-5 flex-shrink-0 text-danger mt-0.5" aria-hidden="true" />
      <div className="flex-1 text-sm">
        <p className="font-medium">{title}</p>
        <p className="text-ink-muted">{message}</p>
      </div>
      {onDismiss && (
        <button
          type="button"
          onClick={onDismiss}
          className="text-ink-muted hover:text-ink text-sm underline decoration-dotted"
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
    <p role="alert" className="mt-1 text-xs text-danger">
      {message}
    </p>
  );
}

/** Wraps a form field, adding a flat danger treatment when `error` is set. */
export function fieldClasses(hasError) {
  return [
    "w-full rounded-button border bg-surface-raised px-3.5 py-2.5 text-base text-ink placeholder:text-ink-muted",
    "transition-colors focus:outline-none focus:ring-2 focus:ring-offset-0",
    hasError
      ? "border-danger focus:ring-danger/20"
      : "border-border focus:border-accent focus:ring-accent/20",
  ].join(" ");
}