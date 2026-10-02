"""Application model — a student applying to an opportunity."""

import enum
from datetime import datetime, timezone

from app.extensions import db


class ApplicationStatus(str, enum.Enum):
    SUBMITTED = "SUBMITTED"   # Default after student applies
    VIEWED = "VIEWED"         # Employer has viewed the application
    SHORTLISTED = "SHORTLISTED"  # Employer shortlisted the candidate
    ACCEPTED = "ACCEPTED"     # Employer accepted the application
    REJECTED = "REJECTED"     # Employer rejected the application
    COMPLETED = "COMPLETED"   # Work completed and reviewed
    WITHDRAWN = "WITHDRAWN"   # Student withdrew application


class Application(db.Model):
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)
    opportunity_id = db.Column(
        db.Integer, db.ForeignKey("gigs.id", ondelete="CASCADE"), nullable=False
    )
    applicant_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    proposal_text = db.Column(db.Text, nullable=True)
    portfolio_url = db.Column(db.String(500), nullable=True)
    status = db.Column(
        db.Enum(ApplicationStatus), default=ApplicationStatus.SUBMITTED, nullable=False, index=True
    )
    viewed_at = db.Column(db.DateTime, nullable=True)
    shortlisted_at = db.Column(db.DateTime, nullable=True)
    accepted_at = db.Column(db.DateTime, nullable=True)
    rejected_at = db.Column(db.DateTime, nullable=True)
    rejection_reason = db.Column(db.Text, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    opportunity = db.relationship("Opportunity", back_populates="applications")
    applicant = db.relationship("User", back_populates="applications")

    __table_args__ = (
        db.UniqueConstraint("opportunity_id", "applicant_id", name="uq_opportunity_applicant"),
        db.Index("idx_applicant_status", "applicant_id", "status"),
        db.Index("idx_opportunity_status", "opportunity_id", "status"),
    )

    def to_dict(self, include_opportunity: bool = False) -> dict:
        data = {
            "id": self.id,
            "opportunity_id": self.opportunity_id,
            "applicant_id": self.applicant_id,
            "proposal_text": self.proposal_text,
            "portfolio_url": self.portfolio_url,
            "status": self.status.value,
            "viewed_at": self.viewed_at.isoformat() if self.viewed_at else None,
            "shortlisted_at": self.shortlisted_at.isoformat() if self.shortlisted_at else None,
            "accepted_at": self.accepted_at.isoformat() if self.accepted_at else None,
            "rejected_at": self.rejected_at.isoformat() if self.rejected_at else None,
            "rejection_reason": self.rejection_reason,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat(),
        }
        if include_opportunity and self.opportunity is not None:
            data["opportunity"] = self.opportunity.to_dict(include_employer=False)
        if self.applicant is not None:
            data["applicant"] = self.applicant.to_public_dict()
        return data

    def __repr__(self) -> str:
        return f"<Application id={self.id} opportunity_id={self.opportunity_id} status={self.status.value}>"