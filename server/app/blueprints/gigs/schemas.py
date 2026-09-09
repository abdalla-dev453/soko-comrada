"""Marshmallow request-validation schemas for the gigs blueprint."""

from marshmallow import Schema, fields, validate

from app.models.gig import GigType


class GigCreateSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=3, max=150))
    description = fields.Str(required=True, validate=validate.Length(min=10, max=5000))
    budget = fields.Decimal(required=True, places=2, validate=validate.Range(min=0))
    gig_type = fields.Str(
        required=True,
        validate=validate.OneOf([t.value for t in GigType]),
    )
    category = fields.Str(required=True, validate=validate.Length(min=2, max=50))
    campus_location = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    is_urgent = fields.Bool(required=False, load_default=False)


class ApplicationCreateSchema(Schema):
    proposal_text = fields.Str(required=False, allow_none=True, validate=validate.Length(max=2000))
