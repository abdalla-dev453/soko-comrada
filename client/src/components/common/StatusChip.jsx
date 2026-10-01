import { CheckCircle, Clock, AlertCircle, Send, Briefcase } from "lucide-react";

const STATUS_CONFIG = {
  OPEN: {
    label: "Open",
    icon: AlertCircle,
    className: "status-open",
  },
  APPLIED: {
    label: "Applied",
    icon: Send,
    className: "status-applied",
  },
  SHORTLISTED: {
    label: "Shortlisted",
    icon: Clock,
    className: "status-shortlisted",
  },
  FUNDED: {
    label: "Funded",
    icon: CheckCircle,
    className: "status-shortlisted",
  },
  IN_PROGRESS: {
    label: "In progress",
    icon: Clock,
    className: "status-in_progress",
  },
  SUBMITTED: {
    label: "Submitted",
    icon: Send,
    className: "status-submitted",
  },
  COMPLETED: {
    label: "Completed",
    icon: CheckCircle,
    className: "status-completed",
  },
  DISPUTED: {
    label: "Disputed",
    icon: AlertCircle,
    className: "status-disputed",
  },
  DRAFT: {
    label: "Draft",
    icon: Briefcase,
    className: "status-draft",
  },
  PENDING_REVIEW: {
    label: "Under review",
    icon: Clock,
    className: "status-pending_review",
  },
};

export function StatusChip({ status, size = "md" }) {
  const config = STATUS_CONFIG[status] || STATUS_CONFIG.OPEN;
  const Icon = config.icon;

  const sizeClasses = {
    sm: "px-2 py-0.5 text-xs",
    md: "px-2.5 py-0.75 text-xs",
  };

  return (
    <span className={`status-chip ${config.className} ${sizeClasses[size]}`}>
      <Icon className="h-3 w-3" aria-hidden="true" />
      <span>{config.label}</span>
    </span>
  );
}
