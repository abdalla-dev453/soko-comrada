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
      className="flex items-start gap-3 rounded-lg bg-danger-100 px-4 py-3 text-text-primary"
    >
      <AlertTriangle className="h-5 w-5 flex-shrink-0 text-danger-700 mt-0.5" aria-hidden="true" />
      <div className="flex-1 text-sm">
        <p className="font-medium">{title}</p>
        <p className="text-text-secondary">{message}</p>
      </div>
      {onDismiss && (
        <button
          type="button"
          onClick={onDismiss}
          className="text-text-secondary hover:text-text-primary text-sm underline decoration-dotted"
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
    <p role="alert" className="mt-1 text-xs text-danger-700">
      {message}
    </p>
  );
}

/** Wraps a form field, adding a flat danger treatment when `error` is set. */
export function fieldClasses(hasError) {
  return [
    "w-full rounded-button border bg-surface px-3.5 py-2.5 text-base text-text-primary placeholder:text-text-secondary",
    "transition-colors focus:outline-none focus:ring-2 focus:ring-offset-0",
    hasError
      ? "border-danger-700 focus:ring-danger-500/20"
      : "border-border focus:border-brand-500 focus:ring-brand-500/20",
  ].join(" ");
}