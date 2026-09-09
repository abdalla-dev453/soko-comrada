import { useState } from "react";

import { Modal } from "../common/Modal";
import { Button } from "../common/Button";
import { FieldError, fieldClasses } from "../common/ErrorBanner";
import { submitPayment } from "../../api/payments";
import { useToast } from "../../hooks/useToast";

const TILL_NUMBER = import.meta.env.VITE_MPESA_TILL_NUMBER || "000000";
const BOOST_FEE = import.meta.env.VITE_BOOST_FEE_KES || "50";

export function BoostModal({ open, onClose, gigId, onSubmitted }) {
  const [mpesaCode, setMpesaCode] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const { toast } = useToast();

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");

    if (mpesaCode.trim().length < 8) {
      setError("Enter the full M-Pesa confirmation code from your SMS.");
      return;
    }

    setSubmitting(true);
    try {
      await submitPayment({ mpesaCode: mpesaCode.trim(), purpose: "BOOST", gigId });
      toast({
        variant: "success",
        title: "Code submitted",
        description: "We'll verify it and boost your gig within a few hours.",
      });
      setMpesaCode("");
      onSubmitted?.();
      onClose();
    } catch (err) {
      setError(err.message || "Couldn't submit that code. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal open={open} onClose={onClose} title="Boost this gig">
      <p className="text-fluid-sm text-ink-muted mb-4">
        Pay <strong className="text-ink">KES {BOOST_FEE}</strong> to Till Number{" "}
        <strong className="text-ink">{TILL_NUMBER}</strong>, then paste the M-Pesa
        confirmation code below. Your gig moves to the top of the feed for 24 hours once
        we verify it.
      </p>

      <form onSubmit={handleSubmit} className="flex flex-col gap-3">
        <div>
          <label htmlFor="mpesa-code" className="text-fluid-sm font-medium text-ink">
            M-Pesa confirmation code
          </label>
          <input
            id="mpesa-code"
            type="text"
            autoComplete="off"
            placeholder="e.g. QAB1CDE2FG"
            value={mpesaCode}
            onChange={(e) => setMpesaCode(e.target.value.toUpperCase())}
            className={`${fieldClasses(Boolean(error))} mt-1 uppercase tracking-wide`}
            aria-invalid={Boolean(error)}
            aria-describedby={error ? "mpesa-code-error" : undefined}
          />
          {error && (
            <span id="mpesa-code-error">
              <FieldError message={error} />
            </span>
          )}
        </div>

        <Button type="submit" loading={submitting} fullWidth>
          Submit code
        </Button>
      </form>
    </Modal>
  );
}