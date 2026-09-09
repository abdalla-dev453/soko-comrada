from datetime import datetime, timezone

import bcrypt 
from app.extensions import db

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    university = db.Column(db.String(100), nullable=False)
    campus_location = db.Column(db.String(100), nullable=False, index=True)

    bio = db.Column(db.Text, nullable=True)
    skills_tags = db.Column(db.String(255), nullable=True)  # comma-separated tags
    avatar_url = db.Column(db.String(500), nullable=True)

    is_verified_entrepreneur = db.Column(db.Boolean, default=False, nullable=False)
    # This is intentionally not accepted from any public request schema.
    is_admin = db.Column(db.Boolean, default=False, nullable=False, index=True)
    avg_rating = db.Column(db.Numeric(3, 2), nullable=True)

    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )


    # Relationships
    gigs_posted = db.relationship(
        "Gig", back_populates="poster", cascade="all, delete-orphan", lazy="dynamic"
    )
    applications = db.relationship(
        "Application", back_populates="applicant", cascade="all, delete-orphan", lazy="dynamic",
    )
    payments = db.relationship(
        "Payment", back_populates="user", cascade="all, delete-orphan", lazy="dynamic"
    )
    reports_filed = db.relationship(
        "Report", back_populates="reporter", cascade="all, delete-orphan", lazy="dynamic", foreign_keys="Report.reporter_id",
    )


    __table_args__ = (db.Index("idx_campus", "campus_location"),)


    # Password handling (bcrypt)
    def set_password(self, raw_password: str) -> None:
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(raw_password.encode("utf-8"), salt).decode("utf-8")


    def check_password(self, raw_password: str) -> bool:
        try:
            return bcrypt.checkpw(
                raw_password.encode("utf-8"), self.password_hash.encode("utf-8")
            )
        except (TypeError, ValueError):
            # A malformed stored hash must never turn into a 500 or a login bypass.
            return False


    def to_public_dict(self) -> dict:
        """Safe representation for API responses — never includes password_hash."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone_number": self.phone_number,
            "university": self.university,
            "campus_location": self.campus_location,
            "bio": self.bio,
            "skills_tags": self.skills_tags.split(",") if self.skills_tags else [],
            "avatar_url": self.avatar_url,
            "is_verified_entrepreneur": self.is_verified_entrepreneur,
            "avg_rating": float(self.avg_rating) if self.avg_rating is not None else None,
            "created_at": self.created_at.isoformat(),
        }

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r}>"
