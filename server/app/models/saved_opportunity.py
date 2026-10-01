"""SavedOpportunity model — bookmarks/favorites for tracking opportunities."""

from datetime import datetime, timezone

from app.extensions import db


class SavedOpportunity(db.Model):
    __tablename__ = "saved_opportunities"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    opportunity_id = db.Column(
        db.Integer, db.ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False
    )
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    user = db.relationship("User", back_populates="saved_opportunities")
    opportunity = db.relationship("Opportunity", back_populates="saved_by")

    __table_args__ = (
        db.UniqueConstraint("user_id", "opportunity_id", name="uq_user_opportunity"),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "opportunity_id": self.opportunity_id,
            "created_at": self.created_at.isoformat(),
        }

    def __repr__(self) -> str:
        return f"<SavedOpportunity user_id={self.user_id} opportunity_id={self.opportunity_id}>"