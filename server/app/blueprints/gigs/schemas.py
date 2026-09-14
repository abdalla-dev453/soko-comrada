"""Marshmallow request-validation schemas for the gigs blueprint."""

from marshmallow import Schema, fields, validate
from app.models.gig import GigType, PriceType


class GigCreateSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=3, max=150))
    description = fields.Str(required=True, validate=validate.Length(min=10, max=5000))
    budget = fields.Decimal(required=True, places=2, validate=validate.Range(min=0))
    price_type = fields.Str(
        required=False,
        load_default="FIXED",
        validate=validate.OneOf([p.value for p in PriceType]),
    )
    gig_type = fields.Str(
        required=True,
        validate=validate.OneOf([t.value for t in GigType]),
    )
    category = fields.Str(required=True, validate=validate.Length(min=2, max=50))
    campus_location = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    landmark = fields.Str(required=False, allow_none=True, validate=validate.Length(max=150))
    is_urgent = fields.Bool(required=False, load_default=False)
    slots_needed = fields.Int(required=False, load_default=1, validate=validate.Range(min=1, max=20))
    deadline = fields.DateTime(required=False, allow_none=True)
    deliverables = fields.List(fields.Str(), required=False, load_default=list)


class GigUpdateSchema(Schema):
    title = fields.Str(required=False, validate=validate.Length(min=3, max=150))
    description = fields.Str(required=False, validate=validate.Length(min=10, max=5000))
    budget = fields.Decimal(required=False, places=2, validate=validate.Range(min=0))
    price_type = fields.Str(
        required=False,
        validate=validate.OneOf([p.value for p in PriceType]),
    )
    category = fields.Str(required=False, validate=validate.Length(min=2, max=50))
    is_urgent = fields.Bool(required=False)
    deadline = fields.DateTime(required=False, allow_none=True)
    deliverables = fields.List(fields.Str(), required=False)


class DisputeCreateSchema(Schema):
    reason = fields.Str(required=True, validate=validate.Length(min=3, max=2000))


class ApplicationCreateSchema(Schema):
    proposal_text = fields.Str(required=False, allow_none=True, validate=validate.Length(max=2000))