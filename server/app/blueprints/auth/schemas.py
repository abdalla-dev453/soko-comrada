"""Marshmallow request-validation schemas for the auth blueprint."""

from marshmallow import Schema, fields, validate, validates
from marshmallow.exceptions import ValidationError


class RegisterSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=12, max=72))
    phone_number = fields.Str(required=True, validate=validate.Length(min=9, max=15))
    university = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    campus_location = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    hostel_location = fields.Str(required=False, allow_none=True, validate=validate.Length(max=100))
    bio = fields.Str(required=False, allow_none=True, validate=validate.Length(max=2000))
    skills_tags = fields.List(fields.Str(), required=False, load_default=list)
    # Phase 10: growth_service.find_referrer looks this up against
    # User.referral_code — invalid/unknown codes are silently ignored
    # (see register()) rather than rejecting signup over a typo.
    referral_code = fields.Str(required=False, allow_none=True, validate=validate.Length(max=10))

    @validates("password")
    def validate_password(self, value, **kwargs):
        if not any(char.isalpha() for char in value) or not any(char.isdigit() for char in value):
            raise ValidationError("Password must contain at least one letter and one number.")


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)


class RefreshSchema(Schema):
    """No body fields — the refresh token itself is the credential,
    passed as a Bearer token. Kept as an explicit schema so the
    blueprint's schema surface stays uniform and self-documenting."""

    pass


class UpdateProfileSchema(Schema):
    name = fields.Str(required=False, validate=validate.Length(min=2, max=100))
    phone_number = fields.Str(required=False, validate=validate.Length(min=9, max=15))
    campus_location = fields.Str(required=False, validate=validate.Length(min=2, max=100))
    hostel_location = fields.Str(required=False, allow_none=True, validate=validate.Length(max=100))
    bio = fields.Str(required=False, allow_none=True, validate=validate.Length(max=2000))
    skills_tags = fields.List(fields.Str(), required=False)
    avatar_url = fields.Url(required=False, allow_none=True, validate=validate.Length(max=500))
    hide_phone_number = fields.Bool(required=False)


class VerifyEmailSchema(Schema):
    token = fields.Str(required=True, validate=validate.Length(min=1, max=200))


class RequestVerificationSchema(Schema):
    email = fields.Email(required=True)


class WhatsAppVerifySchema(Schema):
    phone_number = fields.Str(required=True, validate=validate.Length(min=9, max=15))
    otp = fields.Str(required=True, validate=validate.Length(min=4, max=8))


class PrivacyToggleSchema(Schema):
    hide_phone_number = fields.Bool(required=True)
