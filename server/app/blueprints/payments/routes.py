"""Payments blueprint — M-Pesa code submission for boosts and
entrepreneur subscriptions. Verification itself is manual/admin-side
in the MVP (see admin blueprint) per PRD §5.3/§9.

PRD §12 finding #2: no rate limiting on /api/payments/verify makes
it brute-forceable to guess valid M-Pesa codes. This route is
rate-limited accordingly.
"""

import hmac

from flask import Blueprint, current_app, jsonify, request
from marshmallow import Schema, ValidationError, fields, validate

from app.extensions import db, limiter
from app.models.gig import Gig
from app.models.payment import Payment, PaymentPurpose
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
    gig_id = fields.Int(required=False, allow_none=True)


class StkPushSchema(Schema):
    purpose = fields.Str(
        required=True,
        validate=validate.OneOf([PaymentPurpose.BOOST.value, PaymentPurpose.SUBSCRIPTION.value]),
    )
    gig_id = fields.Int(required=False, allow_none=True)
    phone_number = fields.Str(required=False, allow_none=True, validate=validate.Length(max=15))


class RedeemCreditSchema(Schema):
    gig_id = fields.Int(required=True)


payment_submit_schema = PaymentSubmitSchema()
stk_push_schema = StkPushSchema()
redeem_credit_schema = RedeemCreditSchema()


def _resolve_gig(gig_id):
    if gig_id is None:
        return None, None
    gig = db.session.get(Gig, gig_id)
    if gig is None:
        return None, (jsonify({"error": "not_found", "message": "Gig not found."}), 404)
    return gig, None


@payments_bp.post("/verify")
@limiter.limit("5 per minute")
@load_current_user
def submit_payment_verification(current_user):
    """Despite the name (kept to match the PRD's API surface table
    exactly), this endpoint *submits* a code for an admin to verify —
    see POST /api/admin/payments/<id>/decision for the actual
    verification step. This is the MANUAL fallback path; see
    POST /api/payments/stk-push for the Phase 5 automated flow."""
    try:
        data = payment_submit_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({"error": "validation_error", "message": err.messages}), 422

    purpose = PaymentPurpose(data["purpose"])
    gig, error_response = _resolve_gig(data.get("gig_id"))
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
    """Phase 5: kick off a Daraja STK Push prompt on the payer's
    phone. Returns the PENDING payment immediately — the frontend
    should poll GET /api/payments/mine (or the specific payment) for
    the VERIFIED/REJECTED transition once Safaricom's callback lands.

    Rate-limited the same as the manual /verify endpoint — an
    unrestricted STK-push trigger would let someone spam a phone
    number with payment prompts.
    """
    try:
        data = stk_push_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({"error": "validation_error", "message": err.messages}), 422

    purpose = PaymentPurpose(data["purpose"])
    gig, error_response = _resolve_gig(data.get("gig_id"))
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
    """Public webhook Safaricom POSTs to once the STK Push prompt is
    answered (or times out). No auth — Safaricom can't hold a JWT —
    so this endpoint must tolerate garbage input without crashing
    (see daraja_service.parse_callback) and always return 200 with
    ResultCode acknowledged, or Safaricom will retry indefinitely.
    """
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
    """Phase 10: spend a referral-earned free boost credit instead of
    paying — instant, no M-Pesa round trip at all."""
    try:
        data = redeem_credit_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({"error": "validation_error", "message": err.messages}), 422

    gig, error_response = _resolve_gig(data["gig_id"])
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
    """Allows the frontend to poll a specific payment for status
    transitions — primarily used after an STK Push is initiated to
    detect when Safaricom's callback has landed and the status
    moves from PENDING to VERIFIED or REJECTED."""
    payment = Payment.query.get_or_404(payment_id)
    if payment.user_id != current_user.id:
        return jsonify({"error": "forbidden", "message": "This payment isn't yours."}), 403
    return jsonify({"payment": payment.to_dict()}), 200


@payments_bp.get("/mine")
@load_current_user
def list_my_payments(current_user):
    payments = current_user.payments.order_by(Payment.created_at.desc()).all()
    return jsonify({"payments": [p.to_dict() for p in payments]}), 200
