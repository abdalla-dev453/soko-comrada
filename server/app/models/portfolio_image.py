"""Portfolio image model — service providers upload proof-of-work images."""

from datetime import datetime, timezone

from app.extensions import db


class PortfolioImage(db.Model):
    __tablename__ = "portfolio_images"

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    image_url = db.Column(db.String(500), nullable=False)
    caption = db.Column(db.String(200), nullable=True)
    gig_id = db.Column(
        db.Integer, db.ForeignKey("gigs.id", ondelete="SET NULL"), nullable=True
    )
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    owner = db.relationship("User", back_populates="portfolio_images")
    gig = db.relationship("Gig")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "image_url": self.image_url,
            "caption": self.caption,
            "gig_id": self.gig_id,
            "created_at": self.created_at.isoformat(),
        }

    def __repr__(self) -> str:
        return f"<PortfolioImage id={self.id} owner={self.owner_id}>"
