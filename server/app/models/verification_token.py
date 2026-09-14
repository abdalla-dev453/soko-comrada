"""Verification token model — email/WhatsApp OTP verification."""

import secrets
from datetime import datetime, timedelta, timezone

from app.extensions import db


class VerificationToken(db.Model):
    __tablename__ = "verification_tokens"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    token = db.Column(db.String(64), unique=True, nullable=False, index=True)
    token_type = db.Column(
        db.String(20), nullable=False
    )  # "email", "whatsapp"
    purpose = db.Column(
        db.String(30), nullable=False
    )  # "registration", "whatsapp_link"
    expires_at = db.Column(db.DateTime, nullable=False)
    verified_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    user = db.relationship("User", back_populates="verification_tokens")

    @staticmethod
    def generate_token() -> str:
        return secrets.token_urlsafe(32)

    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) > self.expires_at

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "token_type": self.token_type,
            "purpose": self.purpose,
            "expires_at": self.expires_at.isoformat(),
            "verified_at": self.verified_at.isoformat() if self.verified_at else None,
            "created_at": self.created_at.isoformat(),
        }

    def __repr__(self) -> str:
        return f"<VerificationToken id={self.id} type={self.token_type}>"
