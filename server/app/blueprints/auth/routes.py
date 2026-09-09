"""Auth blueprint — registration restricted to student email domains,
JWT access+refresh issuance, and the authenticated user's own profile.
"""

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
    UpdateProfileSchema,
)
from app.extensions import db, limiter
from app.models.user import User
from app.utils.decorators import load_current_user
from app.utils.validators import validate_phone, validate_student_email

auth_bp = Blueprint("auth", __name__)

register_schema = RegisterSchema()
login_schema = LoginSchema()
update_profile_schema = UpdateProfileSchema()


def _issue_tokens(user: User) -> dict:
    # Authorization is loaded from the database on every protected request;
    # no mutable privilege flags are embedded in a bearer token.
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    return {"access_token": access_token, "refresh_token": refresh_token}


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
        bio=data.get("bio"),
        skills_tags=",".join(data.get("skills_tags") or []) or None,
    )
    user.set_password(data["password"])

    db.session.add(user)
    db.session.commit()

    tokens = _issue_tokens(user)
    return jsonify({"user": user.to_public_dict(), **tokens}), 201


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
    return jsonify({"user": user.to_public_dict(), **tokens}), 200


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    user = db.session.get(User, int(user_id)) if user_id else None
    if user is None:
        return jsonify({"error": "unauthorized", "message": "Account not found."}), 401

    access_token = create_access_token(identity=str(user.id))
    return jsonify({"access_token": access_token}), 200


@auth_bp.get("/me")
@load_current_user
def get_me(current_user: User):
    return jsonify({"user": current_user.to_public_dict()}), 200


@auth_bp.patch("/me")
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

    for field in ("name", "phone_number", "campus_location", "bio", "avatar_url"):
        if field in data:
            setattr(current_user, field, data[field])
    if "skills_tags" in data:
        current_user.skills_tags = ",".join(data["skills_tags"]) or None

    db.session.commit()
    return jsonify({"user": current_user.to_public_dict()}), 200
