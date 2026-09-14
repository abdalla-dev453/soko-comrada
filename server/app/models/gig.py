"""Gig model — a task needed or a skill offered, scoped to a campus.

Extended for the post-MVP roadmap:
  Phase 6  (dispute resolution) — completed_by_poster/completed_by_counterparty,
           completion_requested_at, disputed, dispute_reason, disputed_by_id
  Phase 8  (fulfillment precision) — slots_needed/slots_filled, landmark
  Phase 9  (trust & safety) — flagged_for_review, flag_reason
  Phase 12 (standardized delivery) — price_type, deadline, deliverables
"""

import enum
from datetime import datetime, timedelta, timezone

from app.extensions import db

# How long the non-completing party has to confirm or dispute before a
# gig auto-completes (Phase 6, roadmap §"Dispute resolution").
CONFIRMATION_WINDOW = timedelta(hours=48)


class GigType(str, enum.Enum):
    TASK_NEEDED = "TASK_NEEDED"
    SKILL_OFFERED = "SKILL_OFFERED"


class GigStatus(str, enum.Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    PENDING_CONFIRMATION = "PENDING_CONFIRMATION"
    DISPUTED = "DISPUTED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class PriceType(str, enum.Enum):
    FIXED = "FIXED"
    NEGOTIABLE = "NEGOTIABLE"


class Gig(db.Model):
    __tablename__ = "gigs"

    id = db.Column(db.Integer, primary_key=True)
    poster_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    budget = db.Column(db.Numeric(10, 2), nullable=False)
    price_type = db.Column(
        db.Enum(PriceType), default=PriceType.FIXED, nullable=False, index=True
    )
    gig_type = db.Column(db.Enum(GigType), nullable=False)
    category = db.Column(db.String(50), nullable=False, index=True)
    campus_location = db.Column(db.String(100), nullable=False, index=True)
    # Phase 8: sub-campus precision — free-text landmark ("Gate B", "Hostel 5").
    landmark = db.Column(db.String(150), nullable=True)

    # Phase 12: standardized delivery fields.
    deadline = db.Column(db.DateTime, nullable=True)
    deliverables = db.Column(db.Text, nullable=True)  # comma-separated

    is_urgent = db.Column(db.Boolean, default=False, nullable=False)
    is_boosted = db.Column(db.Boolean, default=False, nullable=False)
    boost_expires_at = db.Column(db.DateTime, nullable=True)

    # Phase 8: multi-person gigs. slots_needed=1 is the MVP's original
    # single-applicant behavior; slots_filled tracks accepted applicants.
    slots_needed = db.Column(db.Integer, default=1, nullable=False)
    slots_filled = db.Column(db.Integer, default=0, nullable=False)

    status = db.Column(
        db.Enum(GigStatus), default=GigStatus.OPEN, nullable=False, index=True
    )

    # Phase 6: two-sided completion + dispute window.
    completed_by_poster = db.Column(db.Boolean, default=False, nullable=False)
    completed_by_counterparty = db.Column(db.Boolean, default=False, nullable=False)
    completion_requested_at = db.Column(db.DateTime, nullable=True)
    disputed = db.Column(db.Boolean, default=False, nullable=False)
    dispute_reason = db.Column(db.Text, nullable=True)
    disputed_by_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Phase 9: pre-publish moderation for high-risk categories (academic
    # integrity). A flagged gig is created but withheld from the public
    # feed until an admin clears it.
    flagged_for_review = db.Column(db.Boolean, default=False, nullable=False)
    flag_reason = db.Column(db.String(255), nullable=True)

    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    poster = db.relationship("User", back_populates="gigs_posted", foreign_keys=[poster_id])
    disputed_by = db.relationship("User", foreign_keys=[disputed_by_id])
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

    def is_full(self) -> bool:
        return self.slots_filled >= self.slots_needed

    def confirmation_deadline(self):
        if self.completion_requested_at is None:
            return None
        requested_at = self.completion_requested_at
        if requested_at.tzinfo is None:
            requested_at = requested_at.replace(tzinfo=timezone.utc)
        return requested_at + CONFIRMATION_WINDOW

    def is_past_confirmation_deadline(self) -> bool:
        deadline = self.confirmation_deadline()
        if deadline is None:
            return False
        return datetime.now(timezone.utc) > deadline

    def to_dict(self, include_poster: bool = True) -> dict:
        data = {
            "id": self.id,
            "poster_id": self.poster_id,
            "title": self.title,
            "description": self.description,
            "budget": float(self.budget),
            "price_type": self.price_type.value,
            "gig_type": self.gig_type.value,
            "category": self.category,
            "campus_location": self.campus_location,
            "landmark": self.landmark,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "deliverables": self.deliverables.split(",") if self.deliverables else [],
            "is_urgent": self.is_urgent,
            "is_boosted": self.is_boost_active(),
            "boost_expires_at": (
                self.boost_expires_at.isoformat() if self.boost_expires_at else None
            ),
            "slots_needed": self.slots_needed,
            "slots_filled": self.slots_filled,
            "status": self.status.value,
            "completed_by_poster": self.completed_by_poster,
            "completed_by_counterparty": self.completed_by_counterparty,
            "confirmation_deadline": (
                self.confirmation_deadline().isoformat()
                if self.confirmation_deadline()
                else None
            ),
            "disputed": self.disputed,
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
                "is_verified_student": self.poster.is_verified_student,
            }
        return data

    def __repr__(self) -> str:
        return f"<Gig id={self.id} title={self.title!r} status={self.status.value}>"
