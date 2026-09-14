"""Payment model — M-Pesa payment records for boosts, subscriptions,
referral credits, and (future) escrow.

Two verification paths now coexist (Phase 5 roadmap item):
  - MANUAL: student submits an M-Pesa confirmation code, an admin
    cross-checks it against the till statement (original MVP flow).
  - STK: Daraja STK Push initiated from the app; Safaricom's callback
    verifies the payment automatically. checkout_request_id is the
    correlation id Daraja returns from the initiate call and echoes
    back in the callback.
"""

import enum
from datetime import datetime, timezone

from app.extensions import db


class PaymentPurpose(str, enum.Enum):
    BOOST = "BOOST"
    SUBSCRIPTION = "SUBSCRIPTION"
    ESCROW = "ESCROW"
    REFERRAL_CREDIT = "REFERRAL_CREDIT"  # Phase 10 — informational ledger entry


class PaymentStatus(str, enum.Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


class PaymentMethod(str, enum.Enum):
    MANUAL = "MANUAL"
    STK_PUSH = "STK_PUSH"
    CREDIT = "CREDIT"  # Phase 10 — redeemed free-boost credit, no M-Pesa involved


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    gig_id = db.Column(
        db.Integer, db.ForeignKey("gigs.id", ondelete="SET NULL"), nullable=True
    )
    # Nullable now: an STK Push payment has no code until the Daraja
    # callback lands, and a redeemed credit never has one at all.
    mpesa_code = db.Column(db.String(15), unique=True, nullable=True, index=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    purpose = db.Column(
        db.Enum(PaymentPurpose), default=PaymentPurpose.BOOST, nullable=False
    )
    status = db.Column(
        db.Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False, index=True
    )
    method = db.Column(
        db.Enum(PaymentMethod), default=PaymentMethod.MANUAL, nullable=False
    )

    # Daraja STK Push correlation fields (Phase 5).
    checkout_request_id = db.Column(db.String(64), unique=True, nullable=True, index=True)
    merchant_request_id = db.Column(db.String(64), nullable=True)
    phone_number = db.Column(db.String(15), nullable=True)

    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    user = db.relationship("User", back_populates="payments")
    gig = db.relationship("Gig", back_populates="payments")

    def to_dict(self) -> dict:
        """Owner-safe payment representation; never disclose a full receipt."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "gig_id": self.gig_id,
            "mpesa_code": self._masked_mpesa_code(),
            "amount": float(self.amount),
            "purpose": self.purpose.value,
            "status": self.status.value,
            "method": self.method.value,
            "checkout_request_id": self.checkout_request_id,
            "created_at": self.created_at.isoformat(),
        }

    def _masked_mpesa_code(self) -> str | None:
        if not self.mpesa_code:
            return None
        return "*" * max(len(self.mpesa_code) - 4, 0) + self.mpesa_code[-4:]

    def to_admin_dict(self) -> dict:
        """The manual-verification queue needs the unmasked receipt."""
        data = self.to_dict()
        data.update({"mpesa_code": self.mpesa_code, "phone_number": self.phone_number})
        return data

    def __repr__(self) -> str:
        return f"<Payment id={self.id} method={self.method.value} status={self.status.value}>"
