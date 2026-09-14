"""Saved listing model — bookmarks/favorites for tracking listings."""

from datetime import datetime, timezone

from app.extensions import db


class SavedListing(db.Model):
    __tablename__ = "saved_listings"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    gig_id = db.Column(
        db.Integer, db.ForeignKey("gigs.id", ondelete="CASCADE"), nullable=False
    )
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    user = db.relationship("User", back_populates="saved_listings")
    gig = db.relationship("Gig")

    __table_args__ = (
        db.UniqueConstraint("user_id", "gig_id", name="uq_saved_user_gig"),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "gig_id": self.gig_id,
            "created_at": self.created_at.isoformat(),
        }

    def __repr__(self) -> str:
        return f"<SavedListing id={self.id} user={self.user_id} gig={self.gig_id}>"
