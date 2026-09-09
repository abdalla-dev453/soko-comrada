"""Marshmallow request-validation schemas for the auth blueprint."""

from marshmallow import Schema, fields, validate


class RegisterSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8, max=128))
    phone_number = fields.Str(required=True, validate=validate.Length(min=9, max=15))
    university = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    campus_location = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    bio = fields.Str(required=False, allow_none=True, validate=validate.Length(max=2000))
    skills_tags = fields.List(fields.Str(), required=False, load_default=list)


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
    bio = fields.Str(required=False, allow_none=True, validate=validate.Length(max=2000))
    skills_tags = fields.List(fields.Str(), required=False)
    avatar_url = fields.Str(required=False, allow_none=True, validate=validate.Length(max=500))

