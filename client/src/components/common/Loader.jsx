import { Loader2 } from "lucide-react";
import clsx from "clsx";

export function Loader({ size = "md", label = "Loading", className }) {
  const dimension = { sm: "h-4 w-4", md: "h-6 w-6", lg: "h-9 w-9" }[size];
  return (
    <span className={clsx("inline-flex items-center gap-2 text-ink-muted", className)}>
      <Loader2 className={clsx(dimension, "animate-spin")} aria-hidden="true" />
      <span className="sr-only">{label}</span>
    </span>
  );
}

export function SectionLoader({ label = "Loading" }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-16 text-ink-muted">
      <Loader2 className="h-7 w-7 animate-spin" aria-hidden="true" />
      <p className="text-fluid-sm">{label}</p>
    </div>
  );
}