"""Payments blueprint — M-Pesa payment records for employer listing fees,
subscriptions, featured listings, and (future) escrow.

Two verification paths:
- MANUAL: employer submits an M-Pesa confirmation code, an admin verifies
  it against the till statement (Phase 1 - lead-generation MVP).
- STK: Daraja STK Push initiated from the app; Safaricom's callback
  verifies the payment automatically.
"""

import hmac

from flask import Blueprint, current_app, jsonify, request
from marshmallow import Schema, ValidationError, fields, validate, EXCLUDE

from app.extensions import db, limiter
from app.models.opportunity import Gig
from app.models.payment import Payment, PaymentPurpose, PaymentStatus
from app.services.daraja_service import DarajaError, parse_callback
from app.services.payment_service import (
    PaymentError,
    handle_daraja_callback,
    initiate_stk_payment,
    redeem_boost_credit,
    submit_payment,
)
from app.utils.decorators import load_current_user

payments_bp = Blueprint("payments", __name__)


class PaymentSubmitSchema(Schema):
    mpesa_code = fields.Str(required=True, validate=validate.Length(min=8, max=15))
    purpose = fields.Str(
        required=True,
        validate=validate.OneOf([p.value for p in PaymentPurpose]),
    )
    gig_id = fields.Int(required=False, allow_none=True, data_key="opportunity_id")


class StkPushSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    purpose = fields.Str(
        required=True,
        validate=validate.OneOf([
            PaymentPurpose.EMPLOYER_LISTING_FEE.value,
            PaymentPurpose.EMPLOYER_SUBSCRIPTION.value,
            PaymentPurpose.SUBSCRIPTION.value,
            PaymentPurpose.FEATURED_LISTING.value,
            PaymentPurpose.BOOST.value,
        ]),
    )
    gig_id = fields.Int(required=False, allow_none=True, data_key="opportunity_id")
    phone_number = fields.Str(required=False, allow_none=True, validate=validate.Length(max=15))


class RedeemCreditSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    gig_id = fields.Int(required=False, allow_none=True)
    opportunity_id = fields.Int(required=False, allow_none=True)


payment_submit_schema = PaymentSubmitSchema()
stk_push_schema = StkPushSchema()
redeem_credit_schema = RedeemCreditSchema()


def _resolve_gig(gig_id):
    if gig_id is None:
        return None, None
    gig = db.session.get(Gig, gig_id)
    if gig is None:
        return None, (jsonify({"error": "not_found", "message": "Opportunity not found."}), 404)
    return gig, None


@payments_bp.post("/verify")
@limiter.limit("5 per minute")
@load_current_user
def submit_payment_verification(current_user):
    """Despite the name, this endpoint *submits* a code for an admin to verify.
    See POST /api/admin/payments/<id>/decision for the actual verification step."""
    try:
        data = payment_submit_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({"error": "validation_error", "message": err.messages}), 422

    purpose = PaymentPurpose(data["purpose"])
    gig, error_response = _resolve_gig(data.get("opportunity_id"))
    if error_response:
        return error_response

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


@payments_bp.post("/stk-push")
@limiter.limit("5 per minute")
@load_current_user
def start_stk_push(current_user):
    """Phase 5: kick off a Daraja STK Push prompt on the payer's phone.
    Returns the PENDING payment immediately — the frontend should poll
    GET /api/payments/mine (or the specific payment) for status transitions."""
    try:
        data = stk_push_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({"error": "validation_error", "message": err.messages}), 422

    purpose = PaymentPurpose(data["purpose"])
    gig, error_response = _resolve_gig(data.get("opportunity_id"))
    if error_response:
        return error_response

    try:
        payment = initiate_stk_payment(
            app_config=current_app.config,
            user=current_user,
            purpose=purpose,
            gig=gig,
            phone_number=data.get("phone_number"),
        )
    except (PaymentError, DarajaError) as err:
        return jsonify({"error": "payment_error", "message": err.message}), err.status_code

    return jsonify({"payment": payment.to_dict()}), 202


@payments_bp.post("/daraja/callback")
def daraja_callback():
    """Public webhook Safaricom POSTs to once the STK Push prompt is answered."""
    callback_secret = current_app.config.get("DARAJA_CALLBACK_SECRET", "")
    if callback_secret and not hmac.compare_digest(request.args.get("token", ""), callback_secret):
        current_app.logger.warning("Rejected Daraja callback with an invalid callback secret.")
        return jsonify({"ResultCode": 1, "ResultDesc": "Unauthorized callback"}), 401

    payload = request.get_json(silent=True) or {}
    try:
        callback_data = parse_callback(payload)
    except DarajaError as err:
        current_app.logger.warning("Rejected malformed Daraja callback: %s", err.message)
        return jsonify({"ResultCode": 1, "ResultDesc": "Malformed payload"}), 400

    handle_daraja_callback(callback_data)
    return jsonify({"ResultCode": 0, "ResultDesc": "Accepted"}), 200


@payments_bp.post("/redeem-credit")
@limiter.limit("10 per hour")
@load_current_user
def redeem_credit(current_user):
    """Phase 10: spend a referral-earned free boost credit instead of paying."""
    try:
        data = redeem_credit_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({"error": "validation_error", "message": err.messages}), 422

    # Support both gig_id and opportunity_id
    gig_id = data.get("opportunity_id") or data.get("gig_id")
    if gig_id is None:
        return jsonify({"error": "validation_error", "message": {"opportunity_id": ["Missing data for required field."]}}), 422

    gig, error_response = _resolve_gig(gig_id)
    if error_response:
        return error_response

    try:
        payment = redeem_boost_credit(user=current_user, gig=gig)
    except PaymentError as err:
        return jsonify({"error": "payment_error", "message": err.message}), err.status_code

    return jsonify({"payment": payment.to_dict(), "remaining_credits": current_user.free_boost_credits}), 200


@payments_bp.get("/<int:payment_id>")
@load_current_user
def get_payment(current_user, payment_id: int):
    """Allows the frontend to poll a specific payment for status transitions."""
    payment = Payment.query.get_or_404(payment_id)
    if payment.user_id != current_user.id:
        return jsonify({"error": "forbidden", "message": "This payment isn't yours."}), 403
    return jsonify({"payment": payment.to_dict()}), 200


@payments_bp.get("/mine")
@load_current_user
def list_my_payments(current_user):
    payments = current_user.payments.order_by(Payment.created_at.desc()).all()
    return jsonify({"payments": [p.to_dict() for p in payments]}), 200