"""Admin blueprint — employer verification, opportunity moderation,
payment verification queue, scam-report queue, and analytics.

Routes:
- POST /api/reports (public, authenticated) - flag an opportunity or user
- GET /api/admin/employers/pending - pending employer verification queue
- POST /api/admin/employers/<id>/verify - verify an employer
- GET /api/admin/opportunities/moderation - opportunities pending review
- PATCH /api/admin/opportunities/<id> - moderate an opportunity
- GET /api/admin/payments/pending - payments pending verification
- POST /api/admin/payments/<id>/decision - verify/reject a payment
- GET /api/admin/reports - scam reports queue
- PATCH /api/admin/reports/<id> - resolve a report
- GET /api/admin/disputes - dispute queue
- POST /api/admin/disputes/<gig_id>/resolve - resolve a dispute
- GET /api/admin/analytics - basic marketplace analytics
"""

from datetime import datetime, timezone
from flask import Blueprint, current_app, jsonify, request
from marshmallow import Schema, ValidationError, fields, validate
from sqlalchemy import func, desc

from app.extensions import db, limiter
from app.models.opportunity import Gig, GigStatus
from app.models.payment import Payment, PaymentStatus, PaymentPurpose
from app.models.report import Report, ReportStatus
from app.models.user import User, UserType
from app.models.employer_profile import EmployerProfile, EmployerVerificationStatus
from app.models.application import Application, ApplicationStatus
from app.services import whatsapp_service
from app.services.dispute_service import DisputeError, resolve_dispute
from app.services.payment_service import verify_payment
from app.utils.decorators import admin_required, load_current_user

admin_bp = Blueprint("admin", __name__)


# ---------------------------------------------------------------------------
# Public: flagging an opportunity or user (POST /api/reports)
# ---------------------------------------------------------------------------

class ReportCreateSchema(Schema):
    reason = fields.Str(required=True, validate=validate.Length(min=3, max=255))
    reported_opportunity_id = fields.Int(required=False, allow_none=True)
    reported_user_id = fields.Int(required=False, allow_none=True)


report_create_schema = ReportCreateSchema()


@admin_bp.post("/reports")
@limiter.limit("10 per hour")
@load_current_user
def create_report(current_user):
    try:
        data = report_create_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({"error": "validation_error", "message": err.messages}), 422

    if not data.get("reported_opportunity_id") and not data.get("reported_user_id"):
        return (
            jsonify(
                {
                    "error": "validation_error",
                    "message": {"reported_opportunity_id": ["Report must target an opportunity, a user, or both."]},
                }
            ),
            422,
        )

    from app.models.report import Report as ReportModel
    if data.get("reported_opportunity_id") and db.session.get(Gig, data["reported_opportunity_id"]) is None:
        return jsonify({"error": "not_found", "message": "Reported opportunity not found."}), 404
    if data.get("reported_user_id") and db.session.get(User, data["reported_user_id"]) is None:
        return jsonify({"error": "not_found", "message": "Reported user not found."}), 404

    report = ReportModel(
        reporter_id=current_user.id,
        reported_opportunity_id=data.get("reported_opportunity_id"),
        reported_user_id=data.get("reported_user_id"),
        reason=data["reason"],
    )
    db.session.add(report)
    db.session.commit()

    return jsonify({"report": report.to_dict()}), 201


# ---------------------------------------------------------------------------
# Admin-only: employer verification queue
# ---------------------------------------------------------------------------

@admin_bp.get("/admin/employers/pending")
@admin_required
def list_pending_employers():
    profiles = (
        EmployerProfile.query.filter_by(verification_status=EmployerVerificationStatus.PENDING)
        .order_by(EmployerProfile.created_at.asc())
        .all()
    )
    return jsonify({
        "employers": [
            {**p.to_dict(), "user": p.user.to_public_dict()}
            for p in profiles
        ]
    }), 200


class EmployerVerificationSchema(Schema):
    approve = fields.Bool(required=True)
    notes = fields.Str(required=False, allow_none=True, validate=validate.Length(max=1000))


employer_verification_schema = EmployerVerificationSchema()


@admin_bp.post("/admin/employers/<int:user_id>/verify")
@limiter.limit("60 per hour")
@admin_required
def verify_employer(user_id: int):
    user = User.query.get_or_404(user_id)
    if user.user_type != UserType.EMPLOYER:
        return jsonify({"error": "validation_error", "message": {"user_id": ["User is not an employer."]}}), 422

    profile = user.employer_profile
    if profile is None:
        profile = EmployerProfile(user_id=user.id)
        db.session.add(profile)
    if profile.verification_status not in (EmployerVerificationStatus.PENDING, EmployerVerificationStatus.UNDER_REVIEW):
        return jsonify({"error": "conflict", "message": "Employer is already verified or rejected."}), 409

    try:
        data = employer_verification_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({"error": "validation_error", "message": err.messages}), 422

    profile.verification_status = EmployerVerificationStatus.VERIFIED if data["approve"] else EmployerVerificationStatus.REJECTED
    profile.verified_at = datetime.now(timezone.utc)
    profile.verification_notes = data.get("notes")
    user.is_verified_employer = data["approve"]
    db.session.add(user)
    db.session.add(profile)
    db.session.commit()

    if data["approve"]:
        from app.services import whatsapp_service
        whatsapp_service.notify_employer_approved(
            current_app.config,
            to_phone=user.phone_number,
            business_name=user.business_name or user.name,
            logger=current_app.logger,
        )

    return jsonify({"user": user.to_private_dict(), "employer_profile": profile.to_dict()}), 200


# ---------------------------------------------------------------------------
# Admin-only: opportunity moderation queue
# ---------------------------------------------------------------------------

@admin_bp.get("/admin/opportunities/moderation")
@admin_required
def list_opportunities_for_moderation():
    gigs = (
        Gig.query.filter(
            (Gig.flagged_for_review.is_(True)) | (Gig.status == GigStatus.PENDING_REVIEW)
        )
        .order_by(Gig.created_at.desc())
        .all()
    )
    return jsonify({"opportunities": [g.to_dict() for g in gigs]}), 200


class OpportunityModerationSchema(Schema):
    status = fields.Str(
        required=True,
        validate=validate.OneOf(["APPROVE", "REJECT"]),
    )
    reason = fields.Str(required=False, allow_none=True, validate=validate.Length(max=500))


opportunity_moderation_schema = OpportunityModerationSchema()


@admin_bp.post("/admin/opportunities/<int:gig_id>/moderate")
@limiter.limit("60 per hour")
@admin_required
def moderate_opportunity(gig_id: int):
    gig = Gig.query.get_or_404(gig_id)

    try:
        data = opportunity_moderation_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({"error": "validation_error", "message": err.messages}), 422

    if data["status"] == "APPROVE":
        gig.status = GigStatus.OPEN
        gig.flagged_for_review = False
        gig.moderated_by_id = None  # Will be set by decorator
        gig.moderated_at = db.func.now()
        gig.rejection_reason = None
    else:
        gig.status = GigStatus.CANCELLED
        gig.flagged_for_review = False
        gig.rejection_reason = data.get("reason") or "Content does not meet platform guidelines."
        gig.moderated_at = db.func.now()

    db.session.add(gig)
    db.session.commit()

    return jsonify({"opportunity": gig.to_dict()}), 200


# ---------------------------------------------------------------------------
# Admin-only: payment verification queue
# ---------------------------------------------------------------------------

@admin_bp.get("/admin/payments/pending")
@admin_required
def list_pending_payments():
    payments = (
        Payment.query.filter_by(status=PaymentStatus.PENDING)
        .order_by(Payment.created_at.asc())
        .all()
    )
    return jsonify({"payments": [p.to_admin_dict() for p in payments]}), 200


class PaymentDecisionSchema(Schema):
    approve = fields.Bool(required=True)


payment_decision_schema = PaymentDecisionSchema()


@admin_bp.post("/admin/payments/<int:payment_id>/decision")
@limiter.limit("60 per hour")
@admin_required
def decide_payment(payment_id: int):
    payment = Payment.query.get_or_404(payment_id)
    if payment.status != PaymentStatus.PENDING:
        return jsonify({"error": "conflict", "message": "This payment was already decided."}), 409

    try:
        data = payment_decision_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({"error": "validation_error", "message": err.messages}), 422

    payment = verify_payment(payment, approve=data["approve"])
    return jsonify({"payment": payment.to_dict()}), 200


# ---------------------------------------------------------------------------
# Admin-only: reports queue
# ---------------------------------------------------------------------------

@admin_bp.get("/admin/reports")
@admin_required
def list_reports():
    status_filter = request.args.get("status")
    query = Report.query
    if status_filter and status_filter in {s.value for s in ReportStatus}:
        query = query.filter(Report.status == ReportStatus(status_filter))
    reports = query.order_by(Report.created_at.desc()).all()
    return jsonify({"reports": [r.to_dict() for r in reports]}), 200


class ReportResolutionSchema(Schema):
    status = fields.Str(
        required=True,
        validate=validate.OneOf([ReportStatus.REVIEWED.value, ReportStatus.DISMISSED.value]),
    )


report_resolution_schema = ReportResolutionSchema()


@admin_bp.patch("/admin/reports/<int:report_id>")
@limiter.limit("60 per hour")
@admin_required
def resolve_report(report_id: int):
    report = Report.query.get_or_404(report_id)

    try:
        data = report_resolution_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({"error": "validation_error", "message": err.messages}), 422

    report.status = ReportStatus(data["status"])
    db.session.add(report)

    # An auto-generated moderation report carries a real consequence
    # for the underlying opportunity, not just a status change on
    # the report itself.
    if report.auto_generated and report.reported_opportunity_id:
        gig = db.session.get(Gig, report.reported_opportunity_id)
        if gig is not None:
            if report.status == ReportStatus.DISMISSED:
                gig.flagged_for_review = False
            elif report.status == ReportStatus.REVIEWED:
                gig.status = GigStatus.CANCELLED
                gig.flagged_for_review = False
            db.session.add(gig)

    db.session.commit()

    return jsonify({"report": report.to_dict()}), 200


# ---------------------------------------------------------------------------
# Admin-only: dispute resolution queue
# ---------------------------------------------------------------------------

@admin_bp.get("/admin/disputes")
@admin_required
def list_disputes():
    gigs = (
        Gig.query.filter_by(status=GigStatus.DISPUTED)
        .order_by(Gig.created_at.asc())
        .all()
    )
    return jsonify({"opportunities": [g.to_dict() for g in gigs]}), 200


class DisputeResolutionSchema(Schema):
    resolution = fields.Str(
        required=True, validate=validate.OneOf(["COMPLETED", "CANCELLED"])
    )


dispute_resolution_schema = DisputeResolutionSchema()


@admin_bp.post("/admin/disputes/<int:gig_id>/resolve")
@limiter.limit("60 per hour")
@admin_required
def resolve_dispute_route(gig_id: int):
    gig = Gig.query.get_or_404(gig_id)

    try:
        data = dispute_resolution_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({"error": "validation_error", "message": err.messages}), 422

    try:
        gig = resolve_dispute(gig, data["resolution"])
    except DisputeError as err:
        return jsonify({"error": "conflict", "message": err.message}), err.status_code

    return jsonify({"opportunity": gig.to_dict(), "gig": gig.to_dict()}), 200


# ---------------------------------------------------------------------------
# Admin-only: analytics dashboard
# ---------------------------------------------------------------------------

@admin_bp.get("/admin/analytics")
@admin_required
def get_analytics():
    from datetime import datetime, timedelta

    now = datetime.utcnow()
    thirty_days_ago = now - timedelta(days=30)

    stats = {
        "users": {
            "total": User.query.count(),
            "students": User.query.filter_by(user_type=UserType.STUDENT).count(),
            "employers": User.query.filter_by(user_type=UserType.EMPLOYER).count(),
            "admins": User.query.filter_by(is_admin=True).count(),
            "verified_students": User.query.filter_by(is_verified_student=True).count(),
            "verified_employers": User.query.filter_by(is_verified_employer=True).count(),
            "new_last_30_days": User.query.filter(User.created_at > thirty_days_ago).count(),
        },
        "opportunities": {
            "total": Gig.query.count(),
            "open": Gig.query.filter_by(status=GigStatus.OPEN).count(),
            "in_progress": Gig.query.filter_by(status=GigStatus.IN_PROGRESS).count(),
            "completed": Gig.query.filter_by(status=GigStatus.COMPLETED).count(),
            "cancelled": Gig.query.filter_by(status=GigStatus.CANCELLED).count(),
            "published_last_30_days": Gig.query.filter(Gig.created_at > thirty_days_ago).count(),
        },
        "applications": {
            "total": Application.query.count(),
            "pending": Application.query.filter_by(status=ApplicationStatus.SUBMITTED).count(),
            "accepted": Application.query.filter_by(status=ApplicationStatus.ACCEPTED).count(),
            "rejected": Application.query.filter_by(status=ApplicationStatus.REJECTED).count(),
        },
        "payments": {
            "total": Payment.query.count(),
            "pending": Payment.query.filter_by(status=PaymentStatus.PENDING).count(),
            "verified": Payment.query.filter_by(status=PaymentStatus.VERIFIED).count(),
            "rejected": Payment.query.filter_by(status=PaymentStatus.REJECTED).count(),
            "gross_volume": float(Payment.query.filter_by(status=PaymentStatus.VERIFIED).with_entities(func.sum(Payment.amount)).scalar() or 0),
        },
        "reports": {
            "total": Report.query.count(),
            "open": Report.query.filter_by(status=ReportStatus.OPEN).count(),
            "reviewed": Report.query.filter_by(status=ReportStatus.REVIEWED).count(),
            "dismissed": Report.query.filter_by(status=ReportStatus.DISMISSED).count(),
        },
    }

    return jsonify({"analytics": stats}), 200