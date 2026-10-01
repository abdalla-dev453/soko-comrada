"""Saved opportunities blueprint — bookmarks/favorites for tracking opportunities."""

from flask import Blueprint, jsonify, request
from marshmallow import Schema, ValidationError, fields

from app.extensions import db, limiter
from app.models.opportunity import Gig
from app.models.saved_opportunity import SavedOpportunity
from app.utils.decorators import load_current_user

saved_listings_bp = Blueprint("saved_listings", __name__)


class SavedOpportunitySchema(Schema):
    opportunity_id = fields.Int(required=True)


saved_opportunity_schema = SavedOpportunitySchema()


@saved_listings_bp.post("")
@limiter.limit("20 per hour")
@load_current_user
def save_opportunity(current_user):
    try:
        data = saved_opportunity_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({"error": "validation_error", "message": err.messages}), 422

    gig = db.session.get(Gig, data["opportunity_id"])
    if gig is None:
        return jsonify({"error": "not_found", "message": "Opportunity not found."}), 404

    existing = SavedOpportunity.query.filter_by(
        user_id=current_user.id, opportunity_id=data["opportunity_id"]
    ).first()
    if existing:
        return jsonify({"saved_opportunity": existing.to_dict(), "saved": True}), 200

    saved = SavedOpportunity(user_id=current_user.id, opportunity_id=data["opportunity_id"])
    db.session.add(saved)
    db.session.commit()

    return jsonify({"saved_opportunity": saved.to_dict(), "saved": True}), 201


@saved_listings_bp.delete("/<int:gig_id>")
@limiter.limit("20 per hour")
@load_current_user
def unsave_opportunity(current_user, gig_id: int):
    saved = SavedOpportunity.query.filter_by(
        user_id=current_user.id, opportunity_id=gig_id
    ).first()
    if saved is None:
        return jsonify({"error": "not_found", "message": "Opportunity not bookmarked."}), 404

    db.session.delete(saved)
    db.session.commit()

    return jsonify({"message": "Opportunity removed from saved."}), 200


@saved_listings_bp.get("")
@load_current_user
def list_saved(current_user):
    saved = (
        SavedOpportunity.query.filter_by(user_id=current_user.id)
        .order_by(SavedOpportunity.created_at.desc())
        .all()
    )
    gig_ids = [s.opportunity_id for s in saved]
    gigs = Gig.query.filter(Gig.id.in_(gig_ids)).all() if gig_ids else []
    return jsonify(
        {
            "saved_opportunities": [s.to_dict() for s in saved],
            "opportunities": [g.to_dict() for g in gigs],
        }
    ), 200


@saved_listings_bp.get("/check/<int:opportunity_id>")
@load_current_user
def check_saved(current_user, opportunity_id: int):
    saved = SavedOpportunity.query.filter_by(
        user_id=current_user.id, opportunity_id=opportunity_id
    ).first()
    return jsonify({"saved": saved is not None}), 200