"""Application model — a student applying to fulfil a posted gig."""

import enum
from datetime import datetime, timezone

from app.extensions import db


class ApplicationStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class Application(db.Model):
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    gig_id = db.Column(
        db.Integer, db.ForeignKey("gigs.id", ondelete="CASCADE"), nullable=False
    )
    applicant_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    proposal_text = db.Column(db.Text, nullable=True)
    status = db.Column(
        db.Enum(ApplicationStatus), default=ApplicationStatus.PENDING, nullable=False
    )
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    gig = db.relationship(
        "Gig", back_populates="applications"
    )
    applicant = db.relationship(
        "User", back_populates="applications"
    )

    __table_args__ = (
        db.UniqueConstraint("gig_id", "applicant_id", name="uq_gig_applicant"),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "gig_id": self.gig_id,
            "applicant": {
                "id": self.applicant.id,
                "name": self.applicant.name,
                "avg_rating": (
                    float(self.applicant.avg_rating)
                    if self.applicant.avg_rating is not None
                    else None
                ),
            },
            "proposal_text": self.proposal_text,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
        }

    def __repr__(self) -> str:
        return f"<Application id={self.id} gig_id={self.gig_id} status={self.status.value}>"
