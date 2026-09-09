"""Report model — flagging a gig or user for spam/scam/abuse (PRD §5.3)."""

import enum
from datetime import datetime, timezone

from app.extensions import db


class ReportStatus(str, enum.Enum):
    OPEN = "OPEN"
    REVIEWED = "REVIEWED"
    DISMISSED = "DISMISSED"


class Report(db.Model):
    __tablename__ = "reports"

    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    reported_gig_id = db.Column(
        db.Integer, db.ForeignKey("gigs.id", ondelete="SET NULL"), nullable=True
    )
    reported_user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    reason = db.Column(db.String(255), nullable=False)
    status = db.Column(
        db.Enum(ReportStatus), default=ReportStatus.OPEN, nullable=False, index=True
    )
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    reporter = db.relationship(
        "User", back_populates="reports_filed", foreign_keys=[reporter_id]
    )
    reported_gig = db.relationship(
        "Gig", back_populates="reports", foreign_keys=[reported_gig_id]
    )
    reported_user = db.relationship("User", foreign_keys=[reported_user_id])

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "reporter_id": self.reporter_id,
            "reported_gig_id": self.reported_gig_id,
            "reported_user_id": self.reported_user_id,
            "reason": self.reason,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
        }

    def __repr__(self) -> str:
        return f"<Report id={self.id} status={self.status.value}>"
