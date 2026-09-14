import { PaymentModal } from "./PaymentModal";

export function SubscriptionModal({ open, onClose, onSubmitted }) {
  return (
    <PaymentModal
      open={open}
      onClose={onClose}
      purpose="SUBSCRIPTION"
      onSuccess={onSubmitted}
    />
  );
}