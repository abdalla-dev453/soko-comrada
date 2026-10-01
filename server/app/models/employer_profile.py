"""EmployerProfile model — extended verification and business details for employers."""

import enum
from datetime import datetime, timezone

from app.extensions import db


class EmployerVerificationStatus(str, enum.Enum):
    PENDING = "PENDING"
    UNDER_REVIEW = "UNDER_REVIEW"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"
    SUSPENDED = "SUSPENDED"


class EmployerProfile(db.Model):
    __tablename__ = "employer_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True
    )

    # Business registration details
    business_registration_number = db.Column(db.String(50), nullable=True)
    business_registration_document_url = db.Column(db.String(500), nullable=True)
    kra_pin = db.Column(db.String(20), nullable=True)
    kra_pin_document_url = db.Column(db.String(500), nullable=True)

    # Business details
    business_type = db.Column(db.String(50), nullable=True)  # e.g., "SME", "Startup", "Corporate"
    industry = db.Column(db.String(100), nullable=True)
    company_size = db.Column(db.String(20), nullable=True)  # e.g., "1-10", "11-50", "51-200", "200+"
    year_established = db.Column(db.Integer, nullable=True)

    # Verification
    verification_status = db.Column(
        db.Enum(EmployerVerificationStatus), default=EmployerVerificationStatus.PENDING, nullable=False, index=True
    )
    verification_notes = db.Column(db.Text, nullable=True)
    verified_at = db.Column(db.DateTime, nullable=True)
    verified_by_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Subscription & billing
    subscription_tier = db.Column(db.String(20), default="FREE", nullable=False)  # FREE, BASIC, PRO, ENTERPRISE
    subscription_expires_at = db.Column(db.DateTime, nullable=True)
    listings_used_this_month = db.Column(db.Integer, default=0, nullable=False)
    listings_limit = db.Column(db.Integer, default=1, nullable=False)  # FREE tier gets 1

    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    user = db.relationship("User", back_populates="employer_profile", foreign_keys="EmployerProfile.user_id")
    verified_by = db.relationship("User", foreign_keys=[verified_by_id])

    def to_dict(self, include_sensitive: bool = False) -> dict:
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "business_registration_number": self.business_registration_number,
            "business_type": self.business_type,
            "industry": self.industry,
            "company_size": self.company_size,
            "year_established": self.year_established,
            "verification_status": self.verification_status.value,
            "verified_at": self.verified_at.isoformat() if self.verified_at else None,
            "subscription_tier": self.subscription_tier,
            "subscription_expires_at": self.subscription_expires_at.isoformat() if self.subscription_expires_at else None,
            "listings_used_this_month": self.listings_used_this_month,
            "listings_limit": self.listings_limit,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
        if include_sensitive:
            data.update({
                "kra_pin": self.kra_pin,
                "verification_notes": self.verification_notes,
            })
        return data

    def __repr__(self) -> str:
        return f"<EmployerProfile id={self.id} user_id={self.user_id} status={self.verification_status.value}>"