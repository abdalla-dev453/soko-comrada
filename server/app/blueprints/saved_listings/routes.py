"""Saved listings blueprint — bookmarks/favorites for tracking listings."""

from flask import Blueprint, jsonify, request
from marshmallow import Schema, ValidationError, fields

from app.extensions import db, limiter
from app.models.gig import Gig
from app.models.saved_listing import SavedListing
from app.utils.decorators import load_current_user

saved_listings_bp = Blueprint("saved_listings", __name__)


class SavedListingSchema(Schema):
    gig_id = fields.Int(required=True)


saved_listing_schema = SavedListingSchema()


@saved_listings_bp.post("")
@limiter.limit("20 per hour")
@load_current_user
def save_listing(current_user):
    try:
        data = saved_listing_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({"error": "validation_error", "message": err.messages}), 422

    gig = db.session.get(Gig, data["gig_id"])
    if gig is None:
        return jsonify({"error": "not_found", "message": "Gig not found."}), 404

    existing = SavedListing.query.filter_by(
        user_id=current_user.id, gig_id=data["gig_id"]
    ).first()
    if existing:
        return jsonify({"saved_listing": existing.to_dict()}), 200

    saved = SavedListing(user_id=current_user.id, gig_id=data["gig_id"])
    db.session.add(saved)
    db.session.commit()

    return jsonify({"saved_listing": saved.to_dict(), "saved": True}), 201


@saved_listings_bp.delete("/<int:gig_id>")
@limiter.limit("20 per hour")
@load_current_user
def unsave_listing(current_user, gig_id: int):
    saved = SavedListing.query.filter_by(
        user_id=current_user.id, gig_id=gig_id
    ).first()
    if saved is None:
        return jsonify({"error": "not_found", "message": "Listing not bookmarked."}), 404

    db.session.delete(saved)
    db.session.commit()

    return jsonify({"message": "Listing removed from saved."}), 200


@saved_listings_bp.get("")
@load_current_user
def list_saved(current_user):
    saved = (
        SavedListing.query.filter_by(user_id=current_user.id)
        .order_by(SavedListing.created_at.desc())
        .all()
    )
    gig_ids = [s.gig_id for s in saved]
    gigs = Gig.query.filter(Gig.id.in_(gig_ids)).all() if gig_ids else []
    return jsonify(
        {
            "saved_listings": [s.to_dict() for s in saved],
            "gigs": [g.to_dict() for g in gigs],
        }
    ), 200


@saved_listings_bp.get("/check/<int:gig_id>")
@load_current_user
def check_saved(current_user, gig_id: int):
    saved = SavedListing.query.filter_by(
        user_id=current_user.id, gig_id=gig_id
    ).first()
    return jsonify({"saved": saved is not None}), 200
