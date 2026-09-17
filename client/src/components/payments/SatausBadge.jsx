import clsx from "clsx";

const STYLES = {
  PENDING: "bg-ink/5 text-ink-muted",
  VERIFIED: "bg-success-soft text-success",
  REJECTED: "bg-danger-soft text-danger",
  OPEN: "bg-warning-soft text-warning",
  REVIEWED: "bg-success-soft text-success",
  DISMISSED: "bg-ink/5 text-ink-muted",
};

export function StatusBadge({ status }) {
  return (
    <span
      className={clsx(
        "flex-shrink-0 rounded-full px-2.5 py-1 text-xs font-medium",
        STYLES[status] || "bg-ink/5 text-ink-muted"
      )}
    >
      {status}
    </span>
  );
}