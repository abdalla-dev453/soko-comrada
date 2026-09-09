"""Reviews blueprint — post-completion two-way star rating + text
review (PRD §5.3), and keeping User.avg_rating in sync so the feed
and profile can show it without recomputing on every read.
"""

from flask import Blueprint, jsonify, request
from marshmallow import Schema, ValidationError, fields, validate
from sqlalchemy import func

from app.extensions import db
from app.models.application import Application, ApplicationStatus
from app.models.gig import Gig, GigStatus
from app.models.review import Review
from app.models.user import User
from app.utils.decorators import load_current_user

reviews_bp = Blueprint("reviews", __name__)


class ReviewCreateSchema(Schema):
    gig_id = fields.Int(required=True)
    reviewee_id = fields.Int(required=True)
    rating = fields.Int(required=True, validate=validate.Range(min=1, max=5))
    comment = fields.Str(required=False, allow_none=True, validate=validate.Length(max=2000))


review_create_schema = ReviewCreateSchema()


def _recompute_avg_rating(user: User) -> None:
    avg = (
        db.session.query(func.avg(Review.rating))
        .filter(Review.reviewee_id == user.id)
        .scalar()
    )
    user.avg_rating = round(float(avg), 2) if avg is not None else None
    db.session.add(user)


@reviews_bp.post("")
@load_current_user
def create_review(current_user):
    try:
        data = review_create_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({"error": "validation_error", "message": err.messages}), 422

    gig = db.session.get(Gig, data["gig_id"])
    if gig is None:
        return jsonify({"error": "not_found", "message": "Gig not found."}), 404

    if gig.status != GigStatus.COMPLETED:
        return jsonify({"error": "conflict", "message": "You can only review a completed gig."}), 409

    accepted_application = Application.query.filter_by(
        gig_id=gig.id, status=ApplicationStatus.ACCEPTED
    ).first()
    counterparty_id = (
        accepted_application.applicant_id if accepted_application else None
    )

    participant_ids = {gig.poster_id, counterparty_id} - {None}
    if current_user.id not in participant_ids:
        return jsonify({"error": "forbidden", "message": "Only gig participants can leave a review."}), 403

    if data["reviewee_id"] not in participant_ids or data["reviewee_id"] == current_user.id:
        return jsonify({"error": "validation_error", "message": {"reviewee_id": ["Invalid reviewee for this gig."]}}), 422

    reviewee = db.session.get(User, data["reviewee_id"])
    if reviewee is None:
        return jsonify({"error": "not_found", "message": "Reviewee not found."}), 404

    existing = Review.query.filter_by(gig_id=gig.id, reviewer_id=current_user.id).first()
    if existing is not None:
        return jsonify({"error": "conflict", "message": "You already reviewed this gig."}), 409

    review = Review(
        gig_id=gig.id,
        reviewer_id=current_user.id,
        reviewee_id=reviewee.id,
        rating=data["rating"],
        comment=data.get("comment"),
    )
    db.session.add(review)
    db.session.flush()

    _recompute_avg_rating(reviewee)
    db.session.commit()

    return jsonify({"review": review.to_dict()}), 201


@reviews_bp.get("/user/<int:user_id>")
def list_reviews_for_user(user_id: int):
    User.query.get_or_404(user_id)
    reviews = (
        Review.query.filter_by(reviewee_id=user_id)
        .order_by(Review.created_at.desc())
        .all()
    )
    return jsonify({"reviews": [r.to_dict() for r in reviews]}), 200
