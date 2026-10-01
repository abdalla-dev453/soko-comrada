"""Marshmallow request-validation schemas for the opportunities blueprint."""

from marshmallow import Schema, fields, validate, EXCLUDE
from app.models.opportunity import OpportunityType, CompensationType, WorkArrangement, PriceType


class OpportunityCreateSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    title = fields.Str(required=True, validate=validate.Length(min=3, max=200))
    description = fields.Str(required=True, validate=validate.Length(min=10, max=5000))
    requirements = fields.Str(required=False, allow_none=True, validate=validate.Length(max=2000))
    responsibilities = fields.Str(required=False, allow_none=True, validate=validate.Length(max=2000))
    opportunity_type = fields.Str(
        required=False,
        load_default=OpportunityType.GIG.value,
        validate=validate.OneOf([t.value for t in OpportunityType]),
    )
    gig_type = fields.Str(required=False, allow_none=True)  # legacy alias
    category = fields.Str(required=True, validate=validate.Length(min=2, max=50))
    skills_required = fields.List(fields.Str(), required=False, load_default=list)

    compensation_type = fields.Str(
        required=False,
        load_default=CompensationType.NEGOTIABLE.value,
        validate=validate.OneOf([c.value for c in CompensationType]),
    )
    pay_min = fields.Decimal(required=False, allow_none=True, places=2, validate=validate.Range(min=0))
    pay_max = fields.Decimal(required=False, allow_none=True, places=2, validate=validate.Range(min=0))
    pay_period = fields.Str(required=False, allow_none=True)
    currency = fields.Str(required=False, load_default="KES", validate=validate.Length(max=3))
    budget = fields.Decimal(required=False, allow_none=True, places=2, validate=validate.Range(min=0))
    price_type = fields.Str(
        required=False,
        load_default=PriceType.FIXED.value,
        validate=validate.OneOf([p.value for p in PriceType]),
    )

    work_arrangement = fields.Str(
        required=False,
        load_default=WorkArrangement.ON_SITE.value,
        validate=validate.OneOf([w.value for w in WorkArrangement]),
    )
    location = fields.Str(required=False, allow_none=True, validate=validate.Length(max=200))
    campus_location = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    landmark = fields.Str(required=False, allow_none=True, validate=validate.Length(max=150))

    deadline = fields.DateTime(required=False, allow_none=True)
    start_date = fields.DateTime(required=False, allow_none=True)
    end_date = fields.DateTime(required=False, allow_none=True)
    duration_weeks = fields.Int(required=False, allow_none=True, validate=validate.Range(min=1, max=104))
    positions_available = fields.Int(required=False, allow_none=True, validate=validate.Range(min=1, max=50))
    slots_needed = fields.Int(required=False, allow_none=True, validate=validate.Range(min=1, max=50))

    is_urgent = fields.Bool(required=False, load_default=False)
    deliverables = fields.List(fields.Str(), required=False, load_default=list)


class OpportunityUpdateSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    title = fields.Str(required=False, validate=validate.Length(min=3, max=200))
    description = fields.Str(required=False, validate=validate.Length(min=10, max=5000))
    requirements = fields.Str(required=False, allow_none=True, validate=validate.Length(max=2000))
    responsibilities = fields.Str(required=False, allow_none=True, validate=validate.Length(max=2000))
    category = fields.Str(required=False, validate=validate.Length(min=2, max=50))
    skills_required = fields.List(fields.Str(), required=False)
    compensation_type = fields.Str(required=False, validate=validate.OneOf([c.value for c in CompensationType]))
    pay_min = fields.Decimal(required=False, allow_none=True, places=2, validate=validate.Range(min=0))
    pay_max = fields.Decimal(required=False, allow_none=True, places=2, validate=validate.Range(min=0))
    pay_period = fields.Str(required=False, allow_none=True)
    budget = fields.Decimal(required=False, allow_none=True, places=2, validate=validate.Range(min=0))
    price_type = fields.Str(required=False, validate=validate.OneOf([p.value for p in PriceType]))
    work_arrangement = fields.Str(required=False, validate=validate.OneOf([w.value for w in WorkArrangement]))
    location = fields.Str(required=False, allow_none=True, validate=validate.Length(max=200))
    campus_location = fields.Str(required=False, validate=validate.Length(min=2, max=100))
    landmark = fields.Str(required=False, allow_none=True, validate=validate.Length(max=150))
    deadline = fields.DateTime(required=False, allow_none=True)
    start_date = fields.DateTime(required=False, allow_none=True)
    end_date = fields.DateTime(required=False, allow_none=True)
    duration_weeks = fields.Int(required=False, allow_none=True, validate=validate.Range(min=1, max=104))
    positions_available = fields.Int(required=False, validate=validate.Range(min=1, max=50))
    slots_needed = fields.Int(required=False, validate=validate.Range(min=1, max=50))
    is_urgent = fields.Bool(required=False)
    deliverables = fields.List(fields.Str(), required=False)


class OpportunityUpdateSchema(Schema):
    title = fields.Str(required=False, validate=validate.Length(min=3, max=200))
    description = fields.Str(required=False, validate=validate.Length(min=10, max=5000))
    requirements = fields.Str(required=False, allow_none=True, validate=validate.Length(max=2000))
    responsibilities = fields.Str(required=False, allow_none=True, validate=validate.Length(max=2000))
    category = fields.Str(required=False, validate=validate.Length(min=2, max=50))
    skills_required = fields.List(fields.Str(), required=False)
    compensation_type = fields.Str(required=False, validate=validate.OneOf([c.value for c in CompensationType]))
    pay_min = fields.Decimal(required=False, allow_none=True, places=2, validate=validate.Range(min=0))
    pay_max = fields.Decimal(required=False, allow_none=True, places=2, validate=validate.Range(min=0))
    pay_period = fields.Str(required=False, allow_none=True)
    work_arrangement = fields.Str(required=False, validate=validate.OneOf([w.value for w in WorkArrangement]))
    location = fields.Str(required=False, allow_none=True, validate=validate.Length(max=200))
    deadline = fields.DateTime(required=False, allow_none=True)
    start_date = fields.DateTime(required=False, allow_none=True)
    end_date = fields.DateTime(required=False, allow_none=True)
    duration_weeks = fields.Int(required=False, allow_none=True, validate=validate.Range(min=1, max=104))
    positions_available = fields.Int(required=False, validate=validate.Range(min=1, max=50))
    is_urgent = fields.Bool(required=False)
    deliverables = fields.List(fields.Str(), required=False)


class ApplicationCreateSchema(Schema):
    proposal_text = fields.Str(required=False, allow_none=True, validate=validate.Length(max=2000))
    portfolio_url = fields.Url(required=False, allow_none=True, validate=validate.Length(max=500))


class ApplicationStatusUpdateSchema(Schema):
    status = fields.Str(
        required=True,
        validate=validate.OneOf([
            "VIEWED", "SHORTLISTED", "ACCEPTED", "REJECTED", "COMPLETED"
        ]),
    )