"""Messages blueprint — in-app conversation between opportunity posters and applicants."""

from datetime import datetime, timezone
from flask import Blueprint, jsonify, request
from marshmallow import Schema, ValidationError, fields, validate
from sqlalchemy import or_, and_

from app.extensions import db, limiter
from app.models.message import Message
from app.models.opportunity import Gig
from app.models.user import User
from app.models.application import Application
from app.utils.decorators import load_current_user

messages_bp = Blueprint("messages", __name__)


class MessageSendSchema(Schema):
    opportunity_id = fields.Int(required=True)
    recipient_id = fields.Int(required=True)
    content = fields.Str(required=True, validate=validate.Length(min=1, max=5000))
    attachment_url = fields.Str(required=False, allow_none=True, validate=validate.Length(max=500))


message_send_schema = MessageSendSchema()


@messages_bp.post("")
@limiter.limit("60 per hour")
@load_current_user
def send_message(current_user):
    try:
        data = message_send_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({"error": "validation_error", "message": err.messages}), 422

    gig = db.session.get(Gig, data["opportunity_id"])
    if gig is None:
        return jsonify({"error": "not_found", "message": "Opportunity not found."}), 404

    recipient = db.session.get(User, data["recipient_id"])
    if recipient is None:
        return jsonify({"error": "not_found", "message": "Recipient not found."}), 404

    if current_user.id == recipient.id:
        return jsonify({"error": "validation_error", "message": {"recipient_id": ["Cannot message yourself."]}}), 422

    # Verification: sender and recipient must be either the poster and an applicant, or co-participants
    is_poster = (gig.employer_id == current_user.id or gig.poster_id == current_user.id)
    is_recipient_poster = (gig.employer_id == recipient.id or gig.poster_id == recipient.id)

    # Check if either party has applied to the opportunity
    user_app = Application.query.filter_by(opportunity_id=gig.id, applicant_id=current_user.id).first()
    recipient_app = Application.query.filter_by(opportunity_id=gig.id, applicant_id=recipient.id).first()

    has_context = (is_poster and recipient_app is not None) or (is_recipient_poster and user_app is not None) or current_user.is_admin
    if not has_context:
        return jsonify({"error": "forbidden", "message": "Can only message participants of this opportunity."}), 403

    msg = Message(
        opportunity_id=gig.id,
        sender_id=current_user.id,
        recipient_id=recipient.id,
        content=data["content"].strip(),
        attachment_url=data.get("attachment_url"),
    )
    db.session.add(msg)
    db.session.commit()

    return jsonify({"message": msg.to_dict()}), 201


@messages_bp.get("/opportunity/<int:opp_id>")
@load_current_user
def list_opportunity_thread(current_user, opp_id: int):
    gig = db.session.get(Gig, opp_id)
    if gig is None:
        return jsonify({"error": "not_found", "message": "Opportunity not found."}), 404

    other_user_id = request.args.get("with_user", type=int)

    query = Message.query.filter(Message.opportunity_id == opp_id)
    if other_user_id:
        query = query.filter(
            or_(
                and_(Message.sender_id == current_user.id, Message.recipient_id == other_user_id),
                and_(Message.sender_id == other_user_id, Message.recipient_id == current_user.id),
            )
        )
    else:
        query = query.filter(
            or_(Message.sender_id == current_user.id, Message.recipient_id == current_user.id)
        )

    messages = query.order_by(Message.created_at.asc()).all()

    # Mark received messages as read
    for m in messages:
        if m.recipient_id == current_user.id and not m.is_read:
            m.is_read = True
    db.session.commit()

    return jsonify({"messages": [m.to_dict() for m in messages]}), 200


@messages_bp.get("/threads")
@load_current_user
def list_threads(current_user):
    """Returns unique conversation threads for the current user."""
    sent_or_recv = Message.query.filter(
        or_(Message.sender_id == current_user.id, Message.recipient_id == current_user.id)
    ).order_by(Message.created_at.desc()).all()

    threads = {}
    for m in sent_or_recv:
        other_id = m.recipient_id if m.sender_id == current_user.id else m.sender_id
        key = f"{m.opportunity_id}:{other_id}"
        if key not in threads:
            other_user = m.recipient if m.sender_id == current_user.id else m.sender
            threads[key] = {
                "opportunity_id": m.opportunity_id,
                "opportunity_title": m.opportunity.title if m.opportunity else None,
                "other_user": other_user.to_public_dict() if other_user else None,
                "last_message": m.to_dict(),
                "unread_count": 1 if (m.recipient_id == current_user.id and not m.is_read) else 0,
            }
        else:
            if m.recipient_id == current_user.id and not m.is_read:
                threads[key]["unread_count"] += 1

    return jsonify({"threads": list(threads.values())}), 200
