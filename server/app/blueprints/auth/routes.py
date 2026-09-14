"""Auth blueprint — registration restricted to student email domains,
JWT access+refresh issuance, and the authenticated user's own profile.

Extended for Phase 12: email verification, WhatsApp OTP verification,
campus badge issuance, and privacy toggle management.
"""

from datetime import datetime, timedelta, timezone

import secrets

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)
from marshmallow import ValidationError

from app.blueprints.auth.schemas import (
    LoginSchema,
    RegisterSchema,
    RequestVerificationSchema,
    UpdateProfileSchema,
    VerifyEmailSchema,
    WhatsAppVerifySchema,
    PrivacyToggleSchema,
)
from app.extensions import db, limiter
from app.models.user import User
from app.models.verification_token import VerificationToken
from app.services import growth_service
from app.services.notification_service import get_notifications_for_user
from app.utils.decorators import load_current_user
from app.utils.validators import validate_phone, validate_student_email

auth_bp = Blueprint("auth", __name__)

register_schema = RegisterSchema()
login_schema = LoginSchema()
update_profile_schema = UpdateProfileSchema()
verify_email_schema = VerifyEmailSchema()
whatsapp_verify_schema = WhatsAppVerifySchema()
privacy_toggle_schema = PrivacyToggleSchema()
request_verify_schema = RequestVerificationSchema()

VERIFICATION_EXPIRY_MINUTES = 15


def _issue_tokens(user: User) -> dict:
    additional_claims = {"is_admin": user.is_admin}
    access_token = create_access_token(
        identity=str(user.id), additional_claims=additional_claims
    )
    refresh_token = create_refresh_token(
        identity=str(user.id), additional_claims=additional_claims
    )
    return {"access_token": access_token, "refresh_token": refresh_token}


def _generate_otp() -> str:
    return f"{secrets.randbelow(900000) + 100000:06d}"


@auth_bp.post("/register")
@limiter.limit("10 per minute")
def register():
    try:
        data = register_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({"error": "validation_error", "message": err.messages}), 422

    allowed_domains = current_app.config["ALLOWED_STUDENT_EMAIL_DOMAINS"]
    if not validate_student_email(data["email"], allowed_domains):
        return (
            jsonify(
                {
                    "error": "validation_error",
                    "message": {
                        "email": [
                            "Registration requires a recognized student email domain."
                        ]
                    },
                }
            ),
            422,
        )

    if not validate_phone(data["phone_number"]):
        return (
            jsonify(
                {
                    "error": "validation_error",
                    "message": {"phone_number": ["Enter a valid phone number."]},
                }
            ),
            422,
        )

    if User.query.filter_by(email=data["email"].lower()).first() is not None:
        return (
            jsonify({"error": "conflict", "message": "An account with this email already exists."}),
            409,
        )

    user = User(
        name=data["name"],
        email=data["email"].lower(),
        phone_number=data["phone_number"],
        university=data["university"],
        campus_location=data["campus_location"],
        hostel_location=data.get("hostel_location"),
        bio=data.get("bio"),
        skills_tags=",".join(data.get("skills_tags") or []) or None,
    )
    user.set_password(data["password"])

    db.session.add(user)
    db.session.flush()  # user.id populated for referral linking below

    # Issue a verification token for email
    token = VerificationToken.generate_token()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=VERIFICATION_EXPIRY_MINUTES)
    verification_token = VerificationToken(
        user_id=user.id,
        token=token,
        token_type="email",
        purpose="registration",
        expires_at=expires_at,
    )
    db.session.add(verification_token)

    referrer = growth_service.find_referrer(data.get("referral_code"))
    growth_service.link_referral(user, referrer)

    db.session.commit()

    tokens = _issue_tokens(user)
    return jsonify({
        "user": user.to_private_dict(),
        "verification_required": True,
        **tokens,
    }), 201


@auth_bp.post("/login")
@limiter.limit("10 per minute")
def login():
    try:
        data = login_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({"error": "validation_error", "message": err.messages}), 422

    user = User.query.filter_by(email=data["email"].lower()).first()
    if user is None or not user.check_password(data["password"]):
        return jsonify({"error": "unauthorized", "message": "Invalid email or password."}), 401

    tokens = _issue_tokens(user)
    return jsonify({"user": user.to_private_dict(), **tokens}), 200


@auth_bp.post("/refresh")
@limiter.limit("20 per minute")
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    user = db.session.get(User, int(user_id)) if user_id else None
    if user is None:
        return jsonify({"error": "unauthorized", "message": "Account not found."}), 401

    access_token = create_access_token(
        identity=str(user.id), additional_claims={"is_admin": user.is_admin}
    )
    return jsonify({"access_token": access_token}), 200


@auth_bp.get("/me")
@load_current_user
def get_me(current_user: User):
    return jsonify({"user": current_user.to_private_dict()}), 200


@auth_bp.patch("/me")
@limiter.limit("20 per minute")
@load_current_user
def update_me(current_user: User):
    try:
        data = update_profile_schema.load(
            request.get_json(silent=True) or {}, partial=True
        )
    except ValidationError as err:
        return jsonify({"error": "validation_error", "message": err.messages}), 422

    if "phone_number" in data and not validate_phone(data["phone_number"]):
        return (
            jsonify(
                {
                    "error": "validation_error",
                    "message": {"phone_number": ["Enter a valid phone number."]},
                }
            ),
            422,
        )

    for field in ("name", "phone_number", "campus_location", "hostel_location", "bio", "avatar_url"):
        if field in data:
            setattr(current_user, field, data[field])
    if "skills_tags" in data:
        current_user.skills_tags = ",".join(data["skills_tags"]) or None
    if "hide_phone_number" in data:
        current_user.hide_phone_number = data["hide_phone_number"]

    db.session.commit()
    return jsonify({"user": current_user.to_private_dict()}), 200


@auth_bp.post("/verify-email")
@limiter.limit("5 per minute")
def verify_email():
    """Verify a user's email using the token sent during registration."""
    try:
        data = verify_email_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({"error": "validation_error", "message": err.messages}), 422

    token_obj = (
        VerificationToken.query.filter_by(token=data["token"], token_type="email")
        .filter(VerificationToken.verified_at.is_(None))
        .first()
    )

    if token_obj is None:
        return jsonify({"error": "not_found", "message": "Invalid or expired verification token."}), 404

    if token_obj.is_expired():
        return jsonify({"error": "expired", "message": "Verification link has expired. Request a new one."}), 410

    user = token_obj.user
    user.is_verified_student = True
    db.session.add(user)

    token_obj.verified_at = datetime.now(timezone.utc)
    db.session.add(token_obj)
    db.session.commit()

    return jsonify({
        "user": user.to_private_dict(),
        "message": "Email verified — welcome to Soko Comrada!",
    }), 200


@auth_bp.post("/request-verification")
@limiter.limit("5 per hour")
def request_verification():
    """Resend a verification email token."""
    try:
        data = request_verify_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({"error": "validation_error", "message": err.messages}), 422

    user = User.query.filter_by(email=data["email"].lower()).first()

    if user.is_verified_student:
        return jsonify({"message": "Email is already verified."}), 200

    # Invalidate existing pending tokens for this user
    existing = VerificationToken.query.filter_by(
        user_id=user.id, token_type="email", verified_at=None
    ).all()
    for t in existing:
        db.session.delete(t)

    token = VerificationToken.generate_token()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=VERIFICATION_EXPIRY_MINUTES)
    verification_token = VerificationToken(
        user_id=user.id,
        token=token,
        token_type="email",
        purpose="registration",
        expires_at=expires_at,
    )
    db.session.add(verification_token)
    db.session.commit()

    return jsonify({"message": "Verification link sent to your email."}), 200


@auth_bp.post("/verify-whatsapp")
@limiter.limit("5 per minute")
def verify_whatsapp():
    """Verify a user's WhatsApp number via OTP."""
    try:
        data = whatsapp_verify_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({"error": "validation_error", "message": err.messages}), 422

    user = User.query.filter_by(phone_number=data["phone_number"]).first()
    if user is None:
        return jsonify({"error": "not_found", "message": "No account with this phone number."}), 404

    if user.whatsapp_verified:
        return jsonify({"user": user.to_private_dict(), "message": "WhatsApp already verified."}), 200

    # In a real implementation, send OTP via WhatsApp Business API here.
    # For now, store the OTP in a verification token and return it for
    # development/testing purposes.
    otp = _generate_otp()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=VERIFICATION_EXPIRY_MINUTES)
    token = VerificationToken.generate_token()

    verification_token = VerificationToken(
        user_id=user.id,
        token=token,
        token_type="whatsapp",
        purpose="whatsapp_link",
        expires_at=expires_at,
    )
    # Store OTP as a separate column would be ideal; using token for dev
    # We'll store the OTP in the token field for dev purposes
    verification_token.token = f"{otp}:{token}"
    db.session.add(verification_token)
    db.session.commit()

    return jsonify({
        "message": "WhatsApp OTP sent (dev mode — check server logs)",
        "otp": otp,  # Dev only — remove in production
    }), 200


@auth_bp.post("/whatsapp/verify-otp")
@limiter.limit("5 per minute")
def verify_whatsapp_otp():
    """Verify WhatsApp OTP and link phone number."""
    try:
        data = whatsapp_verify_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({"error": "validation_error", "message": err.messages}), 422

    user = User.query.filter_by(phone_number=data["phone_number"]).first()
    if user is None:
        return jsonify({"error": "not_found", "message": "No account with this phone number."}), 404

    token_obj = (
        VerificationToken.query.filter_by(user_id=user.id, token_type="whatsapp")
        .filter(VerificationToken.verified_at.is_(None))
        .order_by(VerificationToken.created_at.desc())
        .first()
    )

    if token_obj is None or not token_obj.token.startswith(f"{data['otp']}:"):
        return jsonify({"error": "invalid", "message": "Invalid OTP."}), 400

    if token_obj.is_expired():
        return jsonify({"error": "expired", "message": "OTP has expired."}), 410

    user.whatsapp_verified = True
    user.whatsapp_phone = data["phone_number"]
    db.session.add(user)

    token_obj.verified_at = datetime.now(timezone.utc)
    db.session.add(token_obj)
    db.session.commit()

    return jsonify({"user": user.to_private_dict(), "message": "WhatsApp verified!"}), 200


@auth_bp.get("/notifications")
@load_current_user
def get_notifications(current_user: User):
    """Computed-on-read notification feed (PRD §5.5) — see
    services/notification_service.py for why this isn't backed by a
    dedicated table in the MVP schema."""
    items = get_notifications_for_user(current_user.id)
    return jsonify({"notifications": items}), 200


@auth_bp.post("/privacy/toggle")
@limiter.limit("20 per hour")
@load_current_user
def toggle_privacy(current_user: User):
    """Toggle whether the user's phone number is visible to others."""
    try:
        data = privacy_toggle_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({"error": "validation_error", "message": err.messages}), 422

    current_user.hide_phone_number = data["hide_phone_number"]
    db.session.commit()
    return jsonify({"user": current_user.to_private_dict()}), 200
