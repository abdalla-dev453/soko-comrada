import clsx from "clsx";

const STYLES = {
  PENDING: "bg-ink/5 text-ink-muted",
  VERIFIED: "bg-moss-soft text-moss-strong",
  REJECTED: "bg-coral-soft text-coral-strong",
  OPEN: "bg-coral-soft text-coral-strong",
  REVIEWED: "bg-moss-soft text-moss-strong",
  DISMISSED: "bg-ink/5 text-ink-muted",
};

export function StatusBadge({ status }) {
  return (
    <span
      className={clsx(
        "flex-shrink-0 rounded-full px-2.5 py-1 text-fluid-xs font-medium",
        STYLES[status] || "bg-ink/5 text-ink-muted"
      )}
    >
      {status}
    </span>
  );
}