"""Gig model — a task needed or a skill offered, scoped to a campus."""

import enum
from datetime import datetime, timezone

from app.extensions import db


class GigType(str, enum.Enum):
    TASK_NEEDED = "TASK_NEEDED"
    SKILL_OFFERED = "SKILL-OFFERED"

class GigStatus(str, enum.Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class Gig(db.Model):
    __tablename__ = "gigs"

    id = db.Column(db.Integer, primary_key=True)
    poster_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    budget = db.Column(db.Numeric(10, 2), nullable=False)
    gig_type = db.Column(db.Enum(GigType), nullable=False)
    category = db.Column(db.String(50), nullable=False, index=True)
    campus_location = db.Column(db.String(100), nullable=False, index=True)

    is_urgent = db.Column(db.Boolean, default=False, nullable=False)
    is_boosted = db.Column(db.Boolean, default=False, nullable=False)
    boost_expires_at = db.Column(db.DateTime, nullable=True)

    status = db.Column(
        db.Enum(GigStatus), default=GigStatus.OPEN, nullable=False, index=True
    )

    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    poster = db.relationship("User", back_populates="gigs_posted")
    applications = db.relationship(
        "Application", back_populates="gig", cascade="all, delete-orphan", lazy="dynamic"
    )
    reviews = db.relationship(
        "Review", back_populates="gig", cascade="all, delete-orphan", lazy="dynamic"
    )
    payments = db.relationship("Payment", back_populates="gig", lazy="dynamic")
    reports = db.relationship(
        "Report", back_populates="reported_gig", lazy="dynamic",
        foreign_keys="Report.reported_gig_id",
    )

    __table_args__ = (
        db.Index("idx_status_boosted", "status", "is_boosted"),
        db.Index("idx_category", "category"),
        db.Index("idx_gig_campus", "campus_location"),
    )

    def is_boost_active(self) -> bool:
        if not self.is_boosted or self.boost_expires_at is None:
            return False
        expires_at = self.boost_expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        return expires_at > datetime.now(timezone.utc)

    def to_dict(self, include_poster: bool = True) -> dict:
        data = {
            "id": self.id,
            "poster_id": self.poster_id,
            "title": self.title,
            "description": self.description,
            "budget": float(self.budget),
            "gig_type": self.gig_type.value,
            "category": self.category,
            "campus_location": self.campus_location,
            "is_urgent": self.is_urgent,
            "is_boosted": self.is_boost_active(),
            "boost_expires_at": (
                self.boost_expires_at.isoformat() if self.boost_expires_at else None
            ),
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
        }
        if include_poster and self.poster is not None:
            data["poster"] = {
                "id": self.poster.id,
                "name": self.poster.name,
                "avg_rating": (
                    float(self.poster.avg_rating)
                    if self.poster.avg_rating is not None
                    else None
                ),
                "is_verified_entrepreneur": self.poster.is_verified_entrepreneur,
            }
        return data

    def __repr__(self) -> str:
        return f"<Gig id={self.id} title={self.title!r} status={self.status.value}>"
