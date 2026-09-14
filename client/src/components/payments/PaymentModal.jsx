import { useEffect, useState } from "react";
import { Smartphone, Keyboard, Gift, CheckCircle2, Loader2, RefreshCw } from "lucide-react";
import clsx from "clsx";

import { Modal } from "../common/Modal";
import { Button } from "../common/Button";
import { FieldError, fieldClasses } from "../common/ErrorBanner";
import { initiateSTKPush, pollPayment, redeemBoostCredit, submitPayment } from "../../api/payments";
import { useAuth } from "../../hooks/useAuth";
import { useToast } from "../../hooks/useToast";

const TILL = import.meta.env.VITE_MPESA_TILL_NUMBER || "000000";

const FEES = {
  BOOST: import.meta.env.VITE_BOOST_FEE_KES || "50",
  SUBSCRIPTION: import.meta.env.VITE_SUBSCRIPTION_FEE_KES || "200",
};

const PURPOSE_LABELS = {
  BOOST: "Gig boost (24h)",
  SUBSCRIPTION: "Verified entrepreneur badge (7 days)",
};

export function PaymentModal({ open, onClose, purpose, gigId, onSuccess }) {
  const { user, refreshProfile } = useAuth();
  const { toast } = useToast();

  const [method, setMethod] = useState("stk"); // stk | manual | credit
  const [mpesaCode, setMpesaCode] = useState("");
  const [codeError, setCodeError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  // STK Push polling state
  const [pendingPayment, setPendingPayment] = useState(null);
  const [polling, setPolling] = useState(false);
  const [pollCount, setPollCount] = useState(0);

  const fee = FEES[purpose] || "—";
  const label = PURPOSE_LABELS[purpose] || purpose;
  const hasCredits = user?.free_boost_credits > 0 && purpose === "BOOST";

  // Reset state when modal opens
  useEffect(() => {
    if (open) {
      setMethod(hasCredits ? "credit" : "stk");
      setMpesaCode("");
      setCodeError("");
      setPendingPayment(null);
      setPolling(false);
      setPollCount(0);
    }
  }, [open, hasCredits]);

  // Poll for STK result
  useEffect(() => {
    if (!pendingPayment || !polling) return;
    if (pollCount >= 12) {
      setPolling(false);
      toast({
        variant: "error",
        title: "Timeout",
        description: "Didn't get a response from Safaricom. Check your M-Pesa SMS and use the manual code option if the payment went through.",
      });
      setMethod("manual");
      return;
    }
    const timer = setTimeout(async () => {
      try {
        const updated = await pollPayment(pendingPayment.id);
        if (updated.status === "VERIFIED") {
          setPolling(false);
          await refreshProfile();
          toast({ variant: "success", title: "Payment confirmed", description: `${label} activated.` });
          onSuccess?.();
          onClose();
        } else if (updated.status === "REJECTED") {
          setPolling(false);
          toast({ variant: "error", title: "Payment failed", description: "The STK prompt was cancelled or timed out." });
        } else {
          setPollCount((c) => c + 1);
        }
      } catch {
        setPollCount((c) => c + 1);
      }
    }, 5000);
    return () => clearTimeout(timer);
  }, [pendingPayment, polling, pollCount, label, toast, refreshProfile, onSuccess, onClose]);

  const handleSTK = async () => {
    setSubmitting(true);
    try {
      const payment = await initiateSTKPush({ purpose, gigId });
      setPendingPayment(payment);
      setPolling(true);
      toast({ title: "Check your phone", description: "Enter your M-Pesa PIN when prompted." });
    } catch (err) {
      toast({ variant: "error", title: "STK Push failed", description: err.message });
    } finally {
      setSubmitting(false);
    }
  };

  const handleManual = async (e) => {
    e.preventDefault();
    setCodeError("");
    if (mpesaCode.trim().length < 8) {
      setCodeError("Enter the full M-Pesa confirmation code from your SMS.");
      return;
    }
    setSubmitting(true);
    try {
      await submitPayment({ mpesaCode: mpesaCode.trim(), purpose, gigId });
      toast({ variant: "success", title: "Code submitted", description: "An admin will verify it and activate your payment within a few hours." });
      onSuccess?.();
      onClose();
    } catch (err) {
      setCodeError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleCredit = async () => {
    setSubmitting(true);
    try {
      const result = await redeemBoostCredit(gigId);
      await refreshProfile();
      toast({ variant: "success", title: "Credit redeemed", description: `Boost activated. ${result.remaining_credits} credit${result.remaining_credits !== 1 ? "s" : ""} remaining.` });
      onSuccess?.();
      onClose();
    } catch (err) {
      toast({ variant: "error", title: "Couldn't redeem credit", description: err.message });
    } finally {
      setSubmitting(false);
    }
  };

  // Polling UI
  if (polling) {
    return (
      <Modal open={open} onClose={undefined} title="Waiting for payment">
        <div className="flex flex-col items-center gap-4 py-4 text-center">
          <Loader2 className="h-10 w-10 animate-spin text-moss-strong" aria-hidden="true" />
          <p className="text-fluid-sm text-ink">Waiting for Safaricom to confirm…</p>
          <p className="text-fluid-xs text-ink-muted">Enter your M-Pesa PIN on the prompt that appeared on your phone.</p>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => { setPolling(false); setMethod("manual"); }}
          >
            Didn't get a prompt? Enter code manually
          </Button>
        </div>
      </Modal>
    );
  }

  return (
    <Modal open={open} onClose={onClose} title={`Pay for ${label}`}>
      <p className="text-fluid-sm text-ink-muted mb-4">
        <strong className="text-ink">KES {fee}</strong> · Till number{" "}
        <strong className="text-ink">{TILL}</strong>
      </p>

      {/* Method tabs */}
      <div className="flex gap-1 border border-border rounded-lg p-0.5 mb-5">
        {hasCredits && (
          <MethodTab active={method === "credit"} onClick={() => setMethod("credit")} icon={Gift} label="Free credit" />
        )}
        <MethodTab active={method === "stk"} onClick={() => setMethod("stk")} icon={Smartphone} label="Phone prompt" />
        <MethodTab active={method === "manual"} onClick={() => setMethod("manual")} icon={Keyboard} label="Enter code" />
      </div>

      {method === "credit" && (
        <div className="flex flex-col gap-3">
          <div className="rounded-lg bg-marigold-soft border border-marigold/30 px-4 py-3 text-fluid-sm text-ink">
            <p className="font-medium">You have {user?.free_boost_credits} free boost credit{user?.free_boost_credits !== 1 ? "s" : ""}</p>
            <p className="text-ink-muted mt-0.5">Earned by referring classmates. Redeems instantly — no M-Pesa needed.</p>
          </div>
          <Button onClick={handleCredit} loading={submitting} icon={Gift} fullWidth>
            Redeem credit
          </Button>
        </div>
      )}

      {method === "stk" && (
        <div className="flex flex-col gap-3">
          <p className="text-fluid-sm text-ink-muted">
            Tap below and your phone will prompt you to enter your M-Pesa PIN. The payment confirms automatically — no code to copy.
          </p>
          <Button onClick={handleSTK} loading={submitting} icon={Smartphone} fullWidth>
            Send me the prompt
          </Button>
          <button
            type="button"
            onClick={() => setMethod("manual")}
            className="text-fluid-xs text-ink-muted text-center hover:text-ink"
          >
            Not working? Enter code manually instead
          </button>
        </div>
      )}

      {method === "manual" && (
        <form onSubmit={handleManual} className="flex flex-col gap-3">
          <p className="text-fluid-sm text-ink-muted">
            Pay to <strong className="text-ink">Till {TILL}</strong> then paste the confirmation code from your SMS below.
          </p>
          <div>
            <label htmlFor="pm-mpesa-code" className="text-fluid-sm font-medium text-ink">
              M-Pesa confirmation code
            </label>
            <input
              id="pm-mpesa-code"
              type="text"
              autoComplete="off"
              placeholder="e.g. QAB1CDE2FG"
              value={mpesaCode}
              onChange={(e) => setMpesaCode(e.target.value.toUpperCase())}
              className={`${fieldClasses(Boolean(codeError))} mt-1 uppercase tracking-wide`}
            />
            <FieldError message={codeError} />
          </div>
          <Button type="submit" loading={submitting} icon={CheckCircle2} fullWidth>
            Submit code
          </Button>
          <button
            type="button"
            onClick={() => setMethod("stk")}
            className="text-fluid-xs text-ink-muted text-center hover:text-ink inline-flex items-center justify-center gap-1"
          >
            <RefreshCw className="h-3 w-3" aria-hidden="true" /> Try the phone prompt instead
          </button>
        </form>
      )}
    </Modal>
  );
}

function MethodTab({ active, onClick, icon: Icon, label }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={clsx(
        "flex flex-1 items-center justify-center gap-1.5 rounded-md px-2 py-2 text-fluid-xs font-medium transition-colors",
        active ? "bg-ink text-bg" : "text-ink-muted hover:text-ink"
      )}
    >
      <Icon className="h-3.5 w-3.5" aria-hidden="true" />
      {label}
    </button>
  );
}