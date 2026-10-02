"""Payment model — M-Pesa payment records for opportunity applications, employer listing fees,
subscriptions, referral credits, and escrow.

Verification paths:
- MANUAL: user submits an M-Pesa confirmation code, an admin cross-checks it
- STK_PUSH: Daraja STK Push initiated from the app; Safaricom's callback verifies automatically
"""

import enum
from datetime import datetime, timezone

from app.extensions import db


class PaymentPurpose(str, enum.Enum):
    OPPORTUNITY_APPLICATION = "OPPORTUNITY_APPLICATION"
    EMPLOYER_LISTING_FEE = "EMPLOYER_LISTING_FEE"
    EMPLOYER_SUBSCRIPTION = "EMPLOYER_SUBSCRIPTION"
    SUBSCRIPTION = "SUBSCRIPTION"  # Legacy alias value
    ESCROW = "ESCROW"
    REFERRAL_CREDIT = "REFERRAL_CREDIT"
    FEATURED_LISTING = "FEATURED_LISTING"
    BOOST = "BOOST"


class PaymentStatus(str, enum.Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"
    REFUNDED = "REFUNDED"


class PaymentMethod(str, enum.Enum):
    MANUAL = "MANUAL"
    STK_PUSH = "STK_PUSH"
    CREDIT = "CREDIT"  # Redeemed credit, no M-Pesa involved


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    opportunity_id = db.Column(
        db.Integer, db.ForeignKey("gigs.id", ondelete="SET NULL"), nullable=True
    )
    # Nullable: STK Push has no code until callback, credit never has one
    mpesa_code = db.Column(db.String(15), unique=True, nullable=True, index=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    purpose = db.Column(
        db.Enum(PaymentPurpose), default=PaymentPurpose.EMPLOYER_LISTING_FEE, nullable=False
    )
    status = db.Column(
        db.Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False, index=True
    )
    method = db.Column(
        db.Enum(PaymentMethod), default=PaymentMethod.MANUAL, nullable=False
    )

    # Daraja STK Push correlation fields
    checkout_request_id = db.Column(db.String(64), unique=True, nullable=True, index=True)
    merchant_request_id = db.Column(db.String(64), nullable=True)
    phone_number = db.Column(db.String(15), nullable=True)

    # Refund tracking
    refunded_at = db.Column(db.DateTime, nullable=True)
    refund_reason = db.Column(db.Text, nullable=True)

    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    user = db.relationship("User", back_populates="payments")
    opportunity = db.relationship("Opportunity", back_populates="payments")

    def to_dict(self) -> dict:
        """Owner-safe payment representation; never disclose a full receipt."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "opportunity_id": self.opportunity_id,
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
        return f"<Payment id={self.id} purpose={self.purpose.value} status={self.status.value}>"