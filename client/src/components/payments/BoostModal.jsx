import { PaymentModal } from "./PaymentModal";

export function BoostModal({ open, onClose, gigId, onSubmitted }) {
  return (
    <PaymentModal
      open={open}
      onClose={onClose}
      purpose="BOOST"
      gigId={gigId}
      onSuccess={onSubmitted}
    />
  );
}