"""Opportunity (Gig) model — tasks, attachments, internships, part-time, and remote tasks
posted by verified employers, scoped to campus/location.

Extended with PRD fields: opportunity_type, compensation_type, work_arrangement,
verification status, employer relationship.
"""

import enum
from datetime import datetime, timedelta, timezone

from app.extensions import db


class GigType(str, enum.Enum):
    """Legacy alias — maps to OpportunityType values."""
    TASK_NEEDED = "TASK_NEEDED"
    SKILL_OFFERED = "SKILL_OFFERED"


class OpportunityType(str, enum.Enum):
    GIG = "GIG"
    ATTACHMENT = "ATTACHMENT"
    INTERNSHIP = "INTERNSHIP"
    PART_TIME = "PART_TIME"
    REMOTE_TASK = "REMOTE_TASK"


class GigStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PENDING_REVIEW = "PENDING_REVIEW"
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    FILLED = "FILLED"
    PENDING_CONFIRMATION = "PENDING_CONFIRMATION"
    DISPUTED = "DISPUTED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


class PriceType(str, enum.Enum):
    FIXED = "FIXED"
    NEGOTIABLE = "NEGOTIABLE"


class CompensationType(str, enum.Enum):
    PAID = "PAID"
    UNPAID = "UNPAID"
    STIPEND = "STIPEND"
    NEGOTIABLE = "NEGOTIABLE"


class WorkArrangement(str, enum.Enum):
    ON_SITE = "ON_SITE"
    REMOTE = "REMOTE"
    HYBRID = "HYBRID"


class Opportunity(db.Model):
    """Alias for Gig — represents an opportunity posted by an employer."""
    __tablename__ = "opportunities"

    id = db.Column(db.Integer, primary_key=True)
    employer_id = db.Column(
        db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # Basic info
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text, nullable=True)
    responsibilities = db.Column(db.Text, nullable=True)

    # Categorization
    opportunity_type = db.Column(db.Enum(OpportunityType), nullable=False, index=True)
    category = db.Column(db.String(50), nullable=False, index=True)
    skills_required = db.Column(db.Text, nullable=True)

    # Compensation
    compensation_type = db.Column(
        db.Enum(CompensationType), default=CompensationType.NEGOTIABLE, nullable=False, index=True
    )
    pay_min = db.Column(db.Numeric(10, 2), nullable=True)
    pay_max = db.Column(db.Numeric(10, 2), nullable=True)
    pay_period = db.Column(db.String(20), nullable=True)
    currency = db.Column(db.String(3), default="KES", nullable=False)
    budget = db.Column(db.Numeric(10, 2), nullable=True)
    price_type = db.Column(
        db.Enum(PriceType), default=PriceType.FIXED, nullable=False, index=True
    )

    # Work arrangement
    work_arrangement = db.Column(
        db.Enum(WorkArrangement), default=WorkArrangement.ON_SITE, nullable=False, index=True
    )
    location = db.Column(db.String(200), nullable=True)
    campus_location = db.Column(db.String(100), nullable=True, index=True)
    landmark = db.Column(db.String(150), nullable=True)

    # Legacy fields (kept for compatibility)
    poster_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    gig_type = db.Column(db.Enum(GigType), nullable=True)
    is_urgent = db.Column(db.Boolean, default=False, nullable=False)
    is_boosted = db.Column(db.Boolean, default=False, nullable=False)
    boost_expires_at = db.Column(db.DateTime, nullable=True)
    is_featured = db.Column(db.Boolean, default=False, nullable=False)
    featured_expires_at = db.Column(db.DateTime, nullable=True)
    flagged_for_review = db.Column(db.Boolean, default=False, nullable=False)
    flag_reason = db.Column(db.String(255), nullable=True)
    moderated_by_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    moderated_at = db.Column(db.DateTime, nullable=True)
    rejection_reason = db.Column(db.Text, nullable=True)

    # Capacity
    positions_available = db.Column(db.Integer, default=1, nullable=False)
    positions_filled = db.Column(db.Integer, default=0, nullable=False)
    slots_needed = db.Column(db.Integer, default=1, nullable=False)
    slots_filled = db.Column(db.Integer, default=0, nullable=False)

    # Status
    status = db.Column(db.Enum(GigStatus), default=GigStatus.DRAFT, nullable=False, index=True)

    # Two-sided completion + dispute window
    completed_by_poster = db.Column(db.Boolean, default=False, nullable=False)
    completed_by_counterparty = db.Column(db.Boolean, default=False, nullable=False)
    completion_requested_at = db.Column(db.DateTime, nullable=True)
    disputed = db.Column(db.Boolean, default=False, nullable=False)
    dispute_reason = db.Column(db.Text, nullable=True)
    disputed_by_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Timing
    deadline = db.Column(db.DateTime, nullable=True, index=True)
    start_date = db.Column(db.DateTime, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)
    duration_weeks = db.Column(db.Integer, nullable=True)
    deliverables = db.Column(db.Text, nullable=True)

    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False
    )
    published_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    employer = db.relationship("User", back_populates="opportunities_posted", foreign_keys=[employer_id])
    poster = db.relationship("User", foreign_keys=[poster_id])
    moderated_by = db.relationship("User", foreign_keys=[moderated_by_id])
    disputed_by = db.relationship("User", foreign_keys=[disputed_by_id])
    applications = db.relationship(
        "Application", back_populates="opportunity", cascade="all, delete-orphan", lazy="dynamic"
    )
    saved_by = db.relationship(
        "SavedOpportunity", back_populates="opportunity", cascade="all, delete-orphan", lazy="dynamic"
    )
    payments = db.relationship("Payment", back_populates="opportunity", lazy="dynamic")
    reviews = db.relationship(
        "Review", back_populates="opportunity", cascade="all, delete-orphan", lazy="dynamic"
    )
    reports = db.relationship(
        "Report", back_populates="reported_opportunity", lazy="dynamic",
        foreign_keys="Report.reported_opportunity_id",
    )

    __table_args__ = (
        db.Index("idx_status_type", "status", "opportunity_type"),
        db.Index("idx_campus_type", "campus_location", "opportunity_type"),
        db.Index("idx_deadline_status", "deadline", "status"),
        db.Index("idx_compensation", "compensation_type"),
        db.Index("idx_budget", "budget"),
    )

    # Alias for Gig to maintain backward compatibility
    Gig = None

    def is_featured_active(self) -> bool:
        if not self.is_featured or self.featured_expires_at is None:
            return False
        expires_at = self.featured_expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        return expires_at > datetime.now(timezone.utc)

    def is_boost_active(self) -> bool:
        if not self.is_boosted or self.boost_expires_at is None:
            return False
        expires_at = self.boost_expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        return expires_at > datetime.now(timezone.utc)

    def is_open_for_applications(self) -> bool:
        if self.status != GigStatus.OPEN:
            return False
        if self.positions_filled >= self.positions_available:
            return False
        if self.deadline:
            deadline = self.deadline
            if deadline.tzinfo is None:
                deadline = deadline.replace(tzinfo=timezone.utc)
            if datetime.now(timezone.utc) > deadline:
                return False
        return True

    def is_full(self) -> bool:
        return self.positions_filled >= self.positions_available

    def confirmation_deadline(self):
        if self.completion_requested_at is None:
            return None
        requested_at = self.completion_requested_at
        if requested_at.tzinfo is None:
            requested_at = requested_at.replace(tzinfo=timezone.utc)
        return requested_at + timedelta(hours=48)

    def is_past_confirmation_deadline(self) -> bool:
        deadline = self.confirmation_deadline()
        if deadline is None:
            return False
        return datetime.now(timezone.utc) > deadline

    def to_dict(self, include_employer: bool = True) -> dict:
        data = {
            "id": self.id,
            "employer_id": self.employer_id,
            "title": self.title,
            "description": self.description,
            "requirements": self.requirements,
            "responsibilities": self.responsibilities,
            "opportunity_type": self.opportunity_type.value if self.opportunity_type else None,
            "category": self.category,
            "skills_required": self.skills_required.split(",") if self.skills_required else [],
            "compensation_type": self.compensation_type.value,
            "pay_min": float(self.pay_min) if self.pay_min else None,
            "pay_max": float(self.pay_max) if self.pay_max else None,
            "pay_period": self.pay_period,
            "currency": self.currency,
            "budget": float(self.budget) if self.budget else None,
            "price_type": self.price_type.value if self.price_type else None,
            "work_arrangement": self.work_arrangement.value,
            "location": self.location,
            "campus_location": self.campus_location,
            "landmark": self.landmark,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "duration_weeks": self.duration_weeks,
            "positions_available": self.positions_available,
            "positions_filled": self.positions_filled,
            "is_urgent": self.is_urgent,
            "is_featured": self.is_featured_active(),
            "is_boosted": self.is_boost_active(),
            "boost_expires_at": self.boost_expires_at.isoformat() if self.boost_expires_at else None,
            "status": self.status.value,
            "completed_by_poster": self.completed_by_poster,
            "completed_by_counterparty": self.completed_by_counterparty,
            "confirmation_deadline": self.confirmation_deadline().isoformat() if self.confirmation_deadline() else None,
            "disputed": self.disputed,
            "flagged_for_review": self.flagged_for_review,
            "deliverables": self.deliverables.split(",") if self.deliverables else [],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "published_at": self.published_at.isoformat() if self.published_at else None,
        }
        if include_employer and self.employer is not None:
            data["employer"] = self.employer.to_public_dict()
        return data

    def to_admin_dict(self) -> dict:
        data = self.to_dict(include_employer=True)
        data.update({
            "flag_reason": self.flag_reason,
            "moderated_by_id": self.moderated_by_id,
            "moderated_at": self.moderated_at.isoformat() if self.moderated_at else None,
            "rejection_reason": self.rejection_reason,
        })
        return data

    def __repr__(self) -> str:
        return f"<Opportunity id={self.id} title={self.title!r} type={self.opportunity_type} status={self.status.value}>"


# Backward compatibility alias
Gig = Opportunity