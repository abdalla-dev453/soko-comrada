import { AnimatePresence, motion } from "framer-motion";
import { CheckCircle2, AlertCircle, Info, X } from "lucide-react";

import { useToast } from "../../hooks/useToast";
import { toastSlide } from "../../utils/motion";

const ICONS = {
  default: Info,
  success: CheckCircle2,
  error: AlertCircle,
};

const ACCENTS = {
  default: "text-ink-muted",
  success: "text-moss-strong",
  error: "text-coral-strong",
};

export function ToastViewport() {
  const { toasts, dismiss } = useToast();

  return (
    <div
      className="fixed inset-x-0 bottom-20 z-[60] flex flex-col items-center gap-2 px-4 sm:bottom-6 sm:items-end sm:right-6 sm:left-auto sm:px-0"
      aria-live="polite"
      aria-atomic="false"
    >
      <AnimatePresence>
        {toasts.map((t) => {
          const Icon = ICONS[t.variant] ?? Info;
          return (
            <motion.div
              key={t.id}
              layout
              variants={toastSlide}
              initial="hidden"
              animate="show"
              exit="exit"
              role="status"
              className="w-full max-w-sm rounded-xl bg-surface-raised shadow-popover border border-border px-4 py-3 flex items-start gap-3"
            >
              <Icon className={`h-5 w-5 flex-shrink-0 mt-0.5 ${ACCENTS[t.variant]}`} aria-hidden="true" />
              <div className="flex-1 min-w-0">
                {t.title && <p className="text-fluid-sm font-medium truncate">{t.title}</p>}
                {t.description && (
                  <p className="text-fluid-xs text-ink-muted">{t.description}</p>
                )}
              </div>
              <button
                type="button"
                onClick={() => dismiss(t.id)}
                aria-label="Dismiss notification"
                className="text-ink-muted hover:text-ink"
              >
                <X className="h-4 w-4" aria-hidden="true" />
              </button>
            </motion.div>
          );
        })}
      </AnimatePresence>
    </div>
  );
}