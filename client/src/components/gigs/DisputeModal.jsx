import { useState } from "react";
import { ShieldAlert } from "lucide-react";

import { Modal } from "../common/Modal";
import { Button } from "../common/Button";
import { FieldError, fieldClasses } from "../common/ErrorBanner";
import { disputeGig } from "../../api/gigs";
import { useToast } from "../../hooks/useToast";

export function DisputeModal({ open, onClose, gigId, onDisputed }) {
  const { toast } = useToast();
  const [reason, setReason] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    if (reason.trim().length < 10) {
      setError("Describe what happened — at least 10 characters.");
      return;
    }
    setSubmitting(true);
    try {
      await disputeGig(gigId, reason.trim());
      toast({
        variant: "success",
        title: "Dispute filed",
        description: "An admin will review both sides and make a call. You'll be notified.",
      });
      setReason("");
      onDisputed?.();
      onClose();
    } catch (err) {
      setError(err.message || "Couldn't file the dispute.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal open={open} onClose={onClose} title="Dispute this completion">
      <div className="flex items-start gap-2 rounded-lg bg-coral-soft px-3 py-2.5 text-fluid-xs text-ink mb-4">
        <ShieldAlert className="h-4 w-4 flex-shrink-0 text-coral-strong mt-0.5" aria-hidden="true" />
        <span>
          Filing a dispute pauses the completion. An admin reviews both sides' accounts
          and resolves it — don't do this unless work genuinely wasn't done.
        </span>
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col gap-3">
        <div>
          <label htmlFor="dispute-reason" className="text-fluid-sm font-medium text-ink">
            What happened?
          </label>
          <textarea
            id="dispute-reason"
            rows={4}
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            placeholder="The work was never done / payment wasn't agreed on / other party didn't show up…"
            className={`${fieldClasses(Boolean(error))} mt-1 resize-none`}
          />
          <FieldError message={error} />
        </div>
        <Button type="submit" variant="danger" loading={submitting} fullWidth>
          File dispute
        </Button>
      </form>
    </Modal>
  );
}