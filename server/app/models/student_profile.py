"""StudentProfile model — extended portfolio and verification details for students."""

from datetime import datetime, timezone

from app.extensions import db


class StudentProfile(db.Model):
    __tablename__ = "student_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True
    )

    # Education details
    institution = db.Column(db.String(150), nullable=True, index=True)
    campus = db.Column(db.String(100), nullable=True, index=True)
    course = db.Column(db.String(100), nullable=True, index=True)
    year_of_study = db.Column(db.String(20), nullable=True)  # "1", "2", "3", "4", "5", "Graduate"
    expected_graduation_year = db.Column(db.Integer, nullable=True)
    student_id_number = db.Column(db.String(50), nullable=True)
    student_id_document_url = db.Column(db.String(500), nullable=True)

    # Profile / Portfolio
    headline = db.Column(db.String(200), nullable=True)  # Short tagline
    bio = db.Column(db.Text, nullable=True)
    skills = db.Column(db.Text, nullable=True)  # JSON array of skills
    portfolio_url = db.Column(db.String(500), nullable=True)  # External portfolio
    github_url = db.Column(db.String(255), nullable=True)
    linkedin_url = db.Column(db.String(255), nullable=True)
    website_url = db.Column(db.String(255), nullable=True)

    # Verification
    is_verified_student = db.Column(db.Boolean, default=False, nullable=False)
    student_verification_notes = db.Column(db.Text, nullable=True)
    verified_at = db.Column(db.DateTime, nullable=True)
    verified_by_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Preferences
    preferred_categories = db.Column(db.Text, nullable=True)  # JSON array
    preferred_locations = db.Column(db.Text, nullable=True)  # JSON array
    preferred_work_type = db.Column(db.String(20), nullable=True)  # "remote", "on_site", "hybrid"
    min_pay_expectation = db.Column(db.Numeric(10, 2), nullable=True)
    available_for_internship = db.Column(db.Boolean, default=True, nullable=False)
    available_for_attachment = db.Column(db.Boolean, default=True, nullable=False)
    available_for_gig = db.Column(db.Boolean, default=True, nullable=False)
    available_for_part_time = db.Column(db.Boolean, default=True, nullable=False)

    # Stats
    completed_opportunities = db.Column(db.Integer, default=0, nullable=False)
    total_earnings = db.Column(db.Numeric(12, 2), default=0, nullable=False)

    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    user = db.relationship("User", back_populates="student_profile", foreign_keys="StudentProfile.user_id")
    verified_by = db.relationship("User", foreign_keys=[verified_by_id])

    def to_dict(self, include_sensitive: bool = False) -> dict:
        import json
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "institution": self.institution,
            "campus": self.campus,
            "course": self.course,
            "year_of_study": self.year_of_study,
            "expected_graduation_year": self.expected_graduation_year,
            "headline": self.headline,
            "bio": self.bio,
            "skills": json.loads(self.skills) if self.skills else [],
            "portfolio_url": self.portfolio_url,
            "github_url": self.github_url,
            "linkedin_url": self.linkedin_url,
            "website_url": self.website_url,
            "is_verified_student": self.is_verified_student,
            "verified_at": self.verified_at.isoformat() if self.verified_at else None,
            "preferred_categories": json.loads(self.preferred_categories) if self.preferred_categories else [],
            "preferred_locations": json.loads(self.preferred_locations) if self.preferred_locations else [],
            "preferred_work_type": self.preferred_work_type,
            "min_pay_expectation": float(self.min_pay_expectation) if self.min_pay_expectation else None,
            "available_for_internship": self.available_for_internship,
            "available_for_attachment": self.available_for_attachment,
            "available_for_gig": self.available_for_gig,
            "available_for_part_time": self.available_for_part_time,
            "completed_opportunities": self.completed_opportunities,
            "total_earnings": float(self.total_earnings),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
        if include_sensitive:
            data.update({
                "student_id_number": self.student_id_number,
                "student_id_document_url": self.student_id_document_url,
                "student_verification_notes": self.student_verification_notes,
            })
        return data

    def __repr__(self) -> str:
        return f"<StudentProfile id={self.id} user_id={self.user_id} verified={self.is_verified_student}>"