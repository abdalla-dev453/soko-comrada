"""Portfolio images blueprint — service providers upload proof-of-work."""

from flask import Blueprint, jsonify, request
from marshmallow import Schema, ValidationError, fields

from app.extensions import db, limiter
from app.models.gig import Gig
from app.models.portfolio_image import PortfolioImage
from app.utils.decorators import load_current_user

portfolio_bp = Blueprint("portfolio", __name__)


class PortfolioImageSchema(Schema):
    image_url = fields.Str(required=True, validate=fields.validate.Length(min=1, max=500))
    caption = fields.Str(required=False, allow_none=True, validate=fields.validate.Length(max=200))
    gig_id = fields.Int(required=False, allow_none=True)


portfolio_image_schema = PortfolioImageSchema()


@portfolio_bp.post("")
@limiter.limit("10 per hour")
@load_current_user
def upload_portfolio_image(current_user):
    try:
        data = portfolio_image_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({"error": "validation_error", "message": err.messages}), 422

    if data.get("gig_id"):
        gig = db.session.get(Gig, data["gig_id"])
        if gig is None:
            return jsonify({"error": "not_found", "message": "Gig not found."}), 404

    image = PortfolioImage(
        owner_id=current_user.id,
        image_url=data["image_url"],
        caption=data.get("caption"),
        gig_id=data.get("gig_id"),
    )
    db.session.add(image)
    db.session.commit()

    return jsonify({"portfolio_image": image.to_dict()}), 201


@portfolio_bp.get("")
@load_current_user
def list_portfolio_images(current_user):
    images = (
        PortfolioImage.query.filter_by(owner_id=current_user.id)
        .order_by(PortfolioImage.created_at.desc())
        .all()
    )
    return jsonify({"portfolio_images": [i.to_dict() for i in images]}), 200


@portfolio_bp.get("/user/<int:user_id>")
@load_current_user
def list_user_portfolio(current_user, user_id: int):
    images = (
        PortfolioImage.query.filter_by(owner_id=user_id)
        .order_by(PortfolioImage.created_at.desc())
        .all()
    )
    return jsonify({"portfolio_images": [i.to_dict() for i in images]}), 200


@portfolio_bp.delete("/<int:image_id>")
@limiter.limit("10 per hour")
@load_current_user
def delete_portfolio_image(current_user, image_id: int):
    image = PortfolioImage.query.get_or_404(image_id)
    if image.owner_id != current_user.id and not current_user.is_admin:
        return jsonify({"error": "forbidden", "message": "Not your image."}), 403

    db.session.delete(image)
    db.session.commit()

    return jsonify({"message": "Portfolio image deleted."}), 200
