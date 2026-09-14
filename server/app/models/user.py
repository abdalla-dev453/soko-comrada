"""User model — students ("comrades") who post gigs, apply to gigs,
or run a verified micro-business on the platform.

Extended for Phase 10 (referral growth loop): referral_code,
referred_by_id, free_boost_credits.

Extended for Phase 12 (trust & safety): email/WhatsApp verification,
campus badge, privacy toggle, hostel location tagging.
"""

import secrets
import string
from datetime import datetime, timezone

import bcrypt

from app.extensions import db


def _generate_referral_code() -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(7))


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    university = db.Column(db.String(100), nullable=False)
    campus_location = db.Column(db.String(100), nullable=False, index=True)
    hostel_location = db.Column(db.String(100), nullable=True, index=True)

    bio = db.Column(db.Text, nullable=True)
    skills_tags = db.Column(db.String(255), nullable=True)  # comma-separated tags
    avatar_url = db.Column(db.String(500), nullable=True)

    is_verified_entrepreneur = db.Column(db.Boolean, default=False, nullable=False)
    is_verified_student = db.Column(db.Boolean, default=False, nullable=False)
    whatsapp_verified = db.Column(db.Boolean, default=False, nullable=False)
    whatsapp_phone = db.Column(db.String(15), nullable=True)
    hide_phone_number = db.Column(db.Boolean, default=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    avg_rating = db.Column(db.Numeric(3, 2), nullable=True)

    # Phase 10: referral growth loop.
    referral_code = db.Column(
        db.String(10), unique=True, nullable=False, default=_generate_referral_code
    )
    referred_by_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    free_boost_credits = db.Column(db.Integer, default=0, nullable=False)

    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    gigs_posted = db.relationship(
        "Gig",
        back_populates="poster",
        cascade="all, delete-orphan",
        lazy="dynamic",
        foreign_keys="Gig.poster_id",
    )
    applications = db.relationship(
        "Application",
        back_populates="applicant",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    payments = db.relationship(
        "Payment", back_populates="user", cascade="all, delete-orphan", lazy="dynamic"
    )
    reports_filed = db.relationship(
        "Report",
        back_populates="reporter",
        cascade="all, delete-orphan",
        lazy="dynamic",
        foreign_keys="Report.reporter_id",
    )
    referred_users = db.relationship(
        "User",
        backref=db.backref("referred_by", remote_side=[id]),
        foreign_keys=[referred_by_id],
        lazy="dynamic",
    )
    portfolio_images = db.relationship(
        "PortfolioImage",
        back_populates="owner",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    saved_listings = db.relationship(
        "SavedListing",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    verification_tokens = db.relationship(
        "VerificationToken",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    __table_args__ = (db.Index("idx_campus", "campus_location"),)

    # --- Password handling (bcrypt) ---
    def set_password(self, raw_password: str) -> None:
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(raw_password.encode("utf-8"), salt).decode(
            "utf-8"
        )

    def check_password(self, raw_password: str) -> bool:
        return bcrypt.checkpw(
            raw_password.encode("utf-8"), self.password_hash.encode("utf-8")
        )

    def to_public_dict(self) -> dict:
        """Representation safe to expose to another user or the public."""
        return {
            "id": self.id,
            "name": self.name,
            "university": self.university,
            "campus_location": self.campus_location,
            "hostel_location": self.hostel_location,
            "bio": self.bio,
            "skills_tags": self.skills_tags.split(",") if self.skills_tags else [],
            "avatar_url": self.avatar_url,
            "is_verified_entrepreneur": self.is_verified_entrepreneur,
            "is_verified_student": self.is_verified_student,
            "whatsapp_verified": self.whatsapp_verified,
            "avg_rating": float(self.avg_rating) if self.avg_rating is not None else None,
            "created_at": self.created_at.isoformat(),
        }

    def to_private_dict(self) -> dict:
        """Extends to_public_dict with fields only the account owner
        (or an admin) should see — referral code/credits are not
        anyone else's business."""
        data = self.to_public_dict()
        data.update(
            {
                "email": self.email,
                "phone_number": self.phone_number,
                "hide_phone_number": self.hide_phone_number,
                "whatsapp_phone": self.whatsapp_phone,
                "is_admin": self.is_admin,
                "referral_code": self.referral_code,
                "free_boost_credits": self.free_boost_credits,
            }
        )
        return data

    # Kept as an alias so any earlier callers of to_admin_dict still work.
    to_admin_dict = to_private_dict

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r}>"
