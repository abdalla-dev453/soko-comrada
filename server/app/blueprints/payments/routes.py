"""Payments blueprint — M-Pesa code submission for boosts and
entrepreneur subscriptions. Verification itself is manual/admin-side
in the MVP (see admin blueprint) per PRD §5.3/§9.

PRD §12 finding #2: no rate limiting on /api/payments/verify makes
it brute-forceable to guess valid M-Pesa codes. This route is
rate-limited accordingly.
"""

from flask import Blueprint, current_app, jsonify, request
from marshmallow import Schema, ValidationError, fields, validate

from app.extensions import db, limiter
from app.models.gig import Gig
from app.models.payment import Payment, PaymentPurpose
from app.services.payment_service import PaymentError, submit_payment
from app.utils.decorators import load_current_user

payments_bp = Blueprint("payments", __name__)


class PaymentSubmitSchema(Schema):
    mpesa_code = fields.Str(required=True, validate=validate.Length(min=8, max=15))
    purpose = fields.Str(
        required=True,
        validate=validate.OneOf([p.value for p in PaymentPurpose]),
    )
    gig_id = fields.Int(required=False, allow_none=True)


payment_submit_schema = PaymentSubmitSchema()


@payments_bp.post("/verify")
@limiter.limit("5 per minute")
@load_current_user
def submit_payment_verification(current_user):
    """Despite the name (kept to match the PRD's API surface table
    exactly), this endpoint *submits* a code for an admin to verify —
    see POST /api/admin/payments/<id>/decision for the actual
    verification step."""
    try:
        data = payment_submit_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({"error": "validation_error", "message": err.messages}), 422

    purpose = PaymentPurpose(data["purpose"])

    gig = None
    if data.get("gig_id") is not None:
        gig = db.session.get(Gig, data["gig_id"])
        if gig is None:
            return jsonify({"error": "not_found", "message": "Gig not found."}), 404

    try:
        payment = submit_payment(
            app_config=current_app.config,
            user=current_user,
            mpesa_code=data["mpesa_code"],
            purpose=purpose,
            gig=gig,
        )
    except PaymentError as err:
        return jsonify({"error": "payment_error", "message": err.message}), err.status_code

    return jsonify({"payment": payment.to_dict()}), 201


@payments_bp.get("/mine")
@load_current_user
def list_my_payments(current_user):
    payments = current_user.payments.order_by(Payment.created_at.desc()).all()
    return jsonify({"payments": [p.to_dict() for p in payments]}), 200
