"""Payment model — M-Pesa code submissions for boosts, subscriptions,
and (future) escrow. Verified manually by an admin in the MVP
(PRD §5.3 / §9)."""

import enum
from datetime import datetime, timezone

from app.extensions import db

class PaymentPurpose(str,  enum.Enum):
    BOOST = "BOOST"
    SUBSCRIPTION = "SUBSCRIPTION"
    ESCROW = "ESCROW"


class PaymentStatus(str, enum.Enum):
    PENDING ="PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


class Payment(db.Model):
    __tablename__ = "payments"



    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    gig_id = db.Column(
        db.Integer, db.ForeignKey("gigs.id", ondelete="SET NULL"), nullable=True
    )
    mpesa_code = db.Column(db.String(15), unique=True, nullable=False, index=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    purpose = db.Column(
        db.Enum(PaymentPurpose), default=PaymentPurpose.BOOST, nullable=False
    )
    status = db.Column(
        db.Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False, index=True
    )
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    user = db.relationship("User", back_populates="payments")
    gig = db.relationship("Gig", back_populates="payments")

    def to_dict(self, include_mpesa_code: bool = False) -> dict:
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "gig_id": self.gig_id,
            "amount": float(self.amount),
            "purpose": self.purpose.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
        }
        # Confirmation codes are payment credentials. Only the protected admin
        # verification queue receives the full value; account responses receive
        # a recognizable but non-reusable suffix.
        data["mpesa_code"] = self.mpesa_code if include_mpesa_code else f"****{self.mpesa_code[-4:]}"
        return data

    def __repr__(self) -> str:
        return f"<Payment id={self.id} code={self.mpesa_code} status={self.status.value}>"
