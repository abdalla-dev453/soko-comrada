"""Message model — in-app messaging between opportunity posters and applicants/hustlers."""

from datetime import datetime, timezone
from app.extensions import db


class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    opportunity_id = db.Column(
        db.Integer, db.ForeignKey("gigs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sender_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    recipient_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    content = db.Column(db.Text, nullable=False)
    attachment_url = db.Column(db.String(500), nullable=True)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )

    opportunity = db.relationship("Opportunity", foreign_keys=[opportunity_id])
    sender = db.relationship("User", foreign_keys=[sender_id])
    recipient = db.relationship("User", foreign_keys=[recipient_id])

    __table_args__ = (
        db.Index("idx_opp_users", "opportunity_id", "sender_id", "recipient_id"),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "opportunity_id": self.opportunity_id,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "sender_name": self.sender.name if self.sender else None,
            "recipient_name": self.recipient.name if self.recipient else None,
            "content": self.content,
            "attachment_url": self.attachment_url,
            "is_read": self.is_read,
            "created_at": self.created_at.isoformat(),
        }

    def __repr__(self) -> str:
        return f"<Message id={self.id} opp={self.opportunity_id} from={self.sender_id} to={self.recipient_id}>"
