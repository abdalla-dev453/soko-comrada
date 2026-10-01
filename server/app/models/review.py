"""Review model — post-completion two-way star rating + text review."""

from datetime import datetime, timezone

from app.extensions import db


class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    opportunity_id = db.Column(
        db.Integer, db.ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False
    )
    reviewer_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    reviewee_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    rating = db.Column(db.SmallInteger, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    opportunity = db.relationship("Opportunity", back_populates="reviews")
    reviewer = db.relationship("User", foreign_keys=[reviewer_id])
    reviewee = db.relationship("User", foreign_keys=[reviewee_id])

    __table_args__ = (
        db.CheckConstraint("rating BETWEEN 1 AND 5", name="ck_review_rating_range"),
        db.UniqueConstraint("opportunity_id", "reviewer_id", name="uq_opportunity_reviewer"),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "opportunity_id": self.opportunity_id,
            "reviewer_id": self.reviewer_id,
            "reviewee_id": self.reviewee_id,
            "rating": self.rating,
            "comment": self.comment,
            "created_at": self.created_at.isoformat(),
        }

    def __repr__(self) -> str:
        return f"<Review id={self.id} opportunity_id={self.opportunity_id} rating={self.rating}>"