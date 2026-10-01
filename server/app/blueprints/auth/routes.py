"""Auth blueprint — registration for students and employers, JWT access+refresh issuance,
and the authenticated user's own profile.

Registration accepts both student and employer accounts. Employer accounts
require admin verification before posting opportunities.
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
    EmployerRegisterSchema,
    LoginSchema,
    PhoneVerifySchema,
    PrivacyToggleSchema,
    StudentRegisterSchema,
    UpdateProfileSchema,
    VerifyEmailSchema,
    RequestVerificationSchema,
)
from app.extensions import db, limiter
from app.models.user import User, UserType
from app.models.employer_profile import EmployerProfile, EmployerVerificationStatus
from app.models.student_profile import StudentProfile
from app.models.verification_token import VerificationToken
from app.services import growth_service
from app.services.notification_service import get_notifications_for_user
from app.utils.decorators import load_current_user
from app.utils.validators import validate_phone

auth_bp = Blueprint("auth", __name__)

student_register_schema = StudentRegisterSchema()
employer_register_schema = EmployerRegisterSchema()
login_schema = LoginSchema()
update_profile_schema = UpdateProfileSchema()
verify_email_schema = VerifyEmailSchema()
privacy_toggle_schema = PrivacyToggleSchema()
phone_verify_schema = PhoneVerifySchema()
request_verify_schema = RequestVerificationSchema()

VERIFICATION_EXPIRY_MINUTES = 15


def _issue_tokens(user: User) -> dict:
    additional_claims = {"is_admin": user.is_admin, "user_type": user.user_type.value}
    access_token = create_access_token(
        identity=str(user.id), additional_claims=additional_claims
    )
    refresh_token = create_refresh_token(
        identity=str(user.id), additional_claims=additional_claims
    )
    return {"access_token": access_token, "refresh_token": refresh_token}


def _generate_otp() -> str:
    return f"{secrets.randbelow(900000) + 100000:06d}"


@auth_bp.post("/register/student")
@limiter.limit("10 per minute")
def register_student():
    try:
        data = student_register_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({"error": "validation_error", "message": err.messages}), 422

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
        user_type=UserType.STUDENT,
        name=data["name"],
        email=data["email"].lower(),
        phone_number=data["phone_number"],
        university=data["university"],
        campus_location=data["campus_location"],
        hostel_location=data.get("hostel_location"),
        course=data.get("course"),
        year_of_study=data.get("year_of_study"),
        bio=data.get("bio"),
        skills_tags=",".join(data.get("skills_tags") or []) or None,
    )
    user.set_password(data["password"])

    db.session.add(user)
    db.session.flush()

    # Create student profile
    student_profile = StudentProfile(
        user_id=user.id,
        institution=data.get("university"),
        campus=data.get("campus_location"),
        course=data.get("course"),
        year_of_study=data.get("year_of_study"),
    )
    db.session.add(student_profile)

    # Send email verification token
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

    # Send phone OTP
    phone_token = VerificationToken.generate_token()
    phone_expires = datetime.now(timezone.utc) + timedelta(minutes=VERIFICATION_EXPIRY_MINUTES)
    phone_verification = VerificationToken(
        user_id=user.id,
        token=phone_token,
        token_type="phone",
        purpose="phone_verification",
        expires_at=phone_expires,
    )
    db.session.add(phone_verification)

    referrer = growth_service.find_referrer(data.get("referral_code"))
    growth_service.link_referral(user, referrer)

    db.session.commit()

    tokens = _issue_tokens(user)
    return jsonify({
        "user": user.to_private_dict(),
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "verification_required": True,
        "email_verification_token": token,  # For testing - remove in production
    }), 201


@auth_bp.post("/register/employer")
@limiter.limit("5 per minute")
def register_employer():
    try:
        data = employer_register_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({"error": "validation_error", "message": err.messages}), 422

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
        user_type=UserType.EMPLOYER,
        name=data["name"],
        email=data["email"].lower(),
        phone_number=data["phone_number"],
        business_name=data["business_name"],
        business_description=data.get("business_description"),
        business_website=data.get("business_website"),
        business_location=data["business_location"],
        contact_person_name=data["contact_person_name"],
        contact_person_phone=data.get("contact_person_phone"),
        contact_person_email=data.get("contact_person_email"),
    )
    user.set_password(data["password"])

    db.session.add(user)
    db.session.flush()

    # Create employer profile
    employer_profile = EmployerProfile(
        user_id=user.id,
        business_registration_number=data.get("business_registration_number"),
        kra_pin=data.get("kra_pin"),
        business_type=data.get("business_type"),
        industry=data.get("industry"),
        company_size=data.get("company_size"),
        year_established=data.get("year_established"),
        verification_status=EmployerVerificationStatus.PENDING,
    )
    db.session.add(employer_profile)

    db.session.commit()

    tokens = _issue_tokens(user)
    return jsonify({
        "user": user.to_private_dict(),
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "employer_profile": employer_profile.to_dict(),
        "verification_required": True,
        "message": "Employer account registered. You will be notified once your business is verified before you can post opportunities.",
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
        identity=str(user.id), additional_claims={"is_admin": user.is_admin, "user_type": user.user_type.value}
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

    for field in (
        "name", "phone_number", "campus_location", "hostel_location", "bio", "avatar_url",
        "university", "course", "year_of_study",
        "business_name", "business_description", "business_website",
        "business_location", "contact_person_name", "contact_person_phone",
        "contact_person_email",
    ):
        if field in data:
            setattr(current_user, field, data[field])

    if "skills_tags" in data:
        current_user.skills_tags = ",".join(data["skills_tags"]) or None
    if "hide_phone_number" in data:
        current_user.hide_phone_number = data["hide_phone_number"]

    # Update student profile if exists
    if current_user.student_profile and data.get("university") or data.get("course") or data.get("year_of_study"):
        if data.get("university"):
            current_user.student_profile.institution = data["university"]
        if data.get("campus_location"):
            current_user.student_profile.campus = data["campus_location"]
        if data.get("course"):
            current_user.student_profile.course = data["course"]
        if data.get("year_of_study"):
            current_user.student_profile.year_of_study = data["year_of_study"]
        db.session.add(current_user.student_profile)

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
    user.is_verified_email = True
    db.session.add(user)

    token_obj.verified_at = datetime.now(timezone.utc)
    db.session.add(token_obj)

    # If student, set verified_student flag
    if user.user_type == UserType.STUDENT:
        user.is_verified_student = True
        if user.student_profile:
            user.student_profile.is_verified_student = True
        db.session.add(user.student_profile) if user.student_profile else None

    db.session.commit()

    return jsonify({
        "user": user.to_private_dict(),
        "message": "Email verified — welcome to CampusGig Kenya!",
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

    if user.is_verified_email:
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

    return jsonify({"message": "Verification link sent to your email.", "token": token}), 200


@auth_bp.post("/send-phone-otp")
@limiter.limit("5 per minute")
def send_phone_otp():
    """Send OTP to a phone number for verification."""
    try:
        data = phone_verify_schema.load(request.get_json(silent=True) or {}, partial=True)
    except ValidationError as err:
        return jsonify({"error": "validation_error", "message": err.messages}), 422

    phone_number = data.get("phone_number")
    # Invalidate existing OTPs for this purpose
    existing = VerificationToken.query.filter_by(
        token_type="phone", purpose="phone_verification"
    ).all()

    otp = _generate_otp()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=VERIFICATION_EXPIRY_MINUTES)
    verification_token = VerificationToken(
        user_id=None,  # Can be set later by user lookup
        token=f"{otp}:{VerificationToken.generate_token()}",
        token_type="phone",
        purpose="phone_verification",
        expires_at=expires_at,
    )
    db.session.add(verification_token)
    db.session.commit()

    # In production, send OTP via SMS gateway (Twilio, Africa's Talking, etc.)
    return jsonify({
        "message": "OTP sent to your phone.",
        "otp": otp,  # Dev only — remove in production
        "phone_number": phone_number,
    }), 200


@auth_bp.post("/verify-phone-otp")
@limiter.limit("5 per minute")
def verify_phone_otp():
    """Verify a phone number using OTP."""
    try:
        data = phone_verify_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({"error": "validation_error", "message": err.messages}), 422

    token_obj = (
        VerificationToken.query.filter_by(token_type="phone", purpose="phone_verification")
        .filter(VerificationToken.verified_at.is_(None))
        .order_by(VerificationToken.created_at.desc())
        .first()
    )

    if token_obj is None or not token_obj.token.startswith(f"{data['otp']}:"):
        return jsonify({"error": "invalid", "message": "Invalid OTP."}), 400

    if token_obj.is_expired():
        return jsonify({"error": "expired", "message": "OTP has expired."}), 410

    token_obj.verified_at = datetime.now(timezone.utc)
    db.session.add(token_obj)
    db.session.commit()

    return jsonify({"message": "Phone number verified."}), 200


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


@auth_bp.get("/notifications")
@load_current_user
def get_notifications(current_user: User):
    """Computed-on-read notification feed."""
    items = get_notifications_for_user(current_user.id)
    return jsonify({"notifications": items}), 200