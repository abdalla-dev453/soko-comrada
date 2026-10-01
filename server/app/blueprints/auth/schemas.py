"""Marshmallow request-validation schemas for the auth blueprint."""

from marshmallow import Schema, fields, validate, validates
from marshmallow.exceptions import ValidationError


class StudentRegisterSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=12, max=72))
    phone_number = fields.Str(required=True, validate=validate.Length(min=9, max=15))
    university = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    campus_location = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    hostel_location = fields.Str(required=False, allow_none=True, validate=validate.Length(max=100))
    course = fields.Str(required=False, allow_none=True, validate=validate.Length(max=100))
    year_of_study = fields.Str(required=False, allow_none=True, validate=validate.Length(max=20))
    bio = fields.Str(required=False, allow_none=True, validate=validate.Length(max=2000))
    skills_tags = fields.List(fields.Str(), required=False, load_default=list)
    referral_code = fields.Str(required=False, allow_none=True, validate=validate.Length(max=10))

    @validates("password")
    def validate_password(self, value, **kwargs):
        if not any(char.isalpha() for char in value) or not any(char.isdigit() for char in value):
            raise ValidationError("Password must contain at least one letter and one number.")


class EmployerRegisterSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=12, max=72))
    phone_number = fields.Str(required=True, validate=validate.Length(min=9, max=15))

    # Business details
    business_name = fields.Str(required=True, validate=validate.Length(min=2, max=150))
    business_description = fields.Str(required=False, allow_none=True, validate=validate.Length(max=5000))
    business_website = fields.Url(required=False, allow_none=True, validate=validate.Length(max=255))
    business_location = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    business_type = fields.Str(required=False, allow_none=True, validate=validate.Length(max=50))
    industry = fields.Str(required=False, allow_none=True, validate=validate.Length(max=100))
    company_size = fields.Str(required=False, allow_none=True, validate=validate.OneOf(["1-10", "11-50", "51-200", "200+"]))
    year_established = fields.Int(required=False, allow_none=True)

    # Contact person
    contact_person_name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    contact_person_phone = fields.Str(required=True, validate=validate.Length(min=9, max=15))
    contact_person_email = fields.Email(required=True)

    # Registration documents
    business_registration_number = fields.Str(required=False, allow_none=True, validate=validate.Length(max=50))
    kra_pin = fields.Str(required=False, allow_none=True, validate=validate.Length(max=20))

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

    # Student-specific
    university = fields.Str(required=False, allow_none=True, validate=validate.Length(max=100))
    course = fields.Str(required=False, allow_none=True, validate=validate.Length(max=100))
    year_of_study = fields.Str(required=False, allow_none=True, validate=validate.Length(max=20))

    # Employer-specific
    business_name = fields.Str(required=False, allow_none=True, validate=validate.Length(max=150))
    business_description = fields.Str(required=False, allow_none=True, validate=validate.Length(max=5000))
    business_website = fields.Url(required=False, allow_none=True, validate=validate.Length(max=255))
    business_location = fields.Str(required=False, allow_none=True, validate=validate.Length(max=100))
    contact_person_name = fields.Str(required=False, allow_none=True, validate=validate.Length(max=100))
    contact_person_phone = fields.Str(required=False, allow_none=True, validate=validate.Length(min=9, max=15))
    contact_person_email = fields.Email(required=False, allow_none=True)


class VerifyEmailSchema(Schema):
    token = fields.Str(required=True, validate=validate.Length(min=1, max=200))


class RequestVerificationSchema(Schema):
    email = fields.Email(required=True)


class PhoneVerifySchema(Schema):
    phone_number = fields.Str(required=True, validate=validate.Length(min=9, max=15))
    otp = fields.Str(required=True, validate=validate.Length(min=4, max=8))


class PrivacyToggleSchema(Schema):
    hide_phone_number = fields.Bool(required=True)