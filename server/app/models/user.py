"""User model — students and employers on CampusGig Kenya.

Students find income, attachments, internships, and work experience.
Employers post opportunities and hire verified students.

Extended for trust & safety: email/phone verification, campus badge,
privacy toggle, hostel location tagging.
"""

import secrets
import string
from datetime import datetime, timezone
from enum import Enum as PyEnum

import bcrypt

from app.extensions import db


def _generate_referral_code() -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(7))


class UserType(str, PyEnum):
    STUDENT = "STUDENT"
    EMPLOYER = "EMPLOYER"
    ADMIN = "ADMIN"


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    user_type = db.Column(
        db.Enum(UserType), default=UserType.STUDENT, nullable=False, index=True
    )
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)

    # Student-specific fields
    university = db.Column(db.String(100), nullable=True, index=True)
    campus_location = db.Column(db.String(100), nullable=True, index=True)
    hostel_location = db.Column(db.String(100), nullable=True, index=True)
    course = db.Column(db.String(100), nullable=True)
    year_of_study = db.Column(db.String(20), nullable=True)

    bio = db.Column(db.Text, nullable=True)
    skills_tags = db.Column(db.String(500), nullable=True)  # comma-separated tags
    avatar_url = db.Column(db.String(500), nullable=True)

    # Employer-specific fields (for employer user_type)
    business_name = db.Column(db.String(150), nullable=True)
    business_description = db.Column(db.Text, nullable=True)
    business_website = db.Column(db.String(255), nullable=True)
    business_location = db.Column(db.String(100), nullable=True)
    contact_person_name = db.Column(db.String(100), nullable=True)
    contact_person_phone = db.Column(db.String(15), nullable=True)
    contact_person_email = db.Column(db.String(100), nullable=True)

    # Verification & trust
    is_verified_student = db.Column(db.Boolean, default=False, nullable=False)
    is_verified_employer = db.Column(db.Boolean, default=False, nullable=False)
    is_verified_email = db.Column(db.Boolean, default=False, nullable=False)
    is_verified_phone = db.Column(db.Boolean, default=False, nullable=False)
    hide_phone_number = db.Column(db.Boolean, default=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    avg_rating = db.Column(db.Numeric(3, 2), nullable=True)

    @property
    def is_verified_entrepreneur(self) -> bool:
        """Legacy alias for is_verified_employer."""
        return self.is_verified_employer

    # Referral growth loop
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
    opportunities_posted = db.relationship(
        "Opportunity",
        back_populates="employer",
        cascade="all, delete-orphan",
        lazy="dynamic",
        foreign_keys="Opportunity.employer_id",
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
    saved_opportunities = db.relationship(
        "SavedOpportunity",
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
    employer_profile = db.relationship(
        "EmployerProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        foreign_keys="EmployerProfile.user_id",
    )
    student_profile = db.relationship(
        "StudentProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        foreign_keys="StudentProfile.user_id",
    )

    __table_args__ = (
        db.Index("idx_campus", "campus_location"),
        db.Index("idx_user_type", "user_type"),
    )

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
        data = {
            "id": self.id,
            "user_type": self.user_type.value,
            "name": self.name,
            "university": self.university,
            "campus_location": self.campus_location,
            "hostel_location": self.hostel_location,
            "course": self.course,
            "year_of_study": self.year_of_study,
            "bio": self.bio,
            "skills_tags": self.skills_tags.split(",") if self.skills_tags else [],
            "avatar_url": self.avatar_url,
            "is_verified_student": self.is_verified_student,
            "is_verified_employer": self.is_verified_employer,
            "is_verified_email": self.is_verified_email,
            "is_verified_phone": self.is_verified_phone,
            "avg_rating": float(self.avg_rating) if self.avg_rating is not None else None,
            "created_at": self.created_at.isoformat(),
        }
        if self.user_type == UserType.EMPLOYER:
            data.update({
                "business_name": self.business_name,
                "business_description": self.business_description,
                "business_website": self.business_website,
                "business_location": self.business_location,
                "contact_person_name": self.contact_person_name,
            })
        return data

    def to_private_dict(self) -> dict:
        """Extends to_public_dict with fields only the account owner
        (or an admin) should see."""
        data = self.to_public_dict()
        data.update(
            {
                "email": self.email,
                "phone_number": self.phone_number,
                "hide_phone_number": self.hide_phone_number,
                "is_admin": self.is_admin,
                "is_verified_entrepreneur": self.is_verified_employer,
                "referral_code": self.referral_code,
                "free_boost_credits": self.free_boost_credits,
            }
        )
        if self.user_type == UserType.EMPLOYER:
            data.update({
                "business_website": self.business_website,
                "contact_person_phone": self.contact_person_phone,
                "contact_person_email": self.contact_person_email,
            })
        return data

    to_admin_dict = to_private_dict

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r} type={self.user_type.value}>"
