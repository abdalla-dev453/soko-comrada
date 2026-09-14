"""Admin blueprint — the manual verification queue at the heart of
the MVP trust model (PRD §5.3/§9), plus the reports (flagging)
domain.

Registered at url_prefix="/api" (not "/api/admin") in the app
factory, because the Core API Surface table (PRD §11) puts report
creation at the top-level POST /api/reports — not under /api/admin —
even though Report review/resolution is an admin-only action that
belongs in this module alongside payment verification. Routes below
are explicit about which half of that they're in.
"""

from flask import Blueprint, jsonify, request
from marshmallow import Schema, ValidationError, fields, validate

from app.extensions import db, limiter
from app.models.gig import Gig, GigStatus
from app.models.payment import Payment, PaymentStatus
from app.models.report import Report, ReportStatus
from app.models.user import User
from app.services.dispute_service import DisputeError, resolve_dispute
from app.services.payment_service import verify_payment
from app.utils.decorators import admin_required, load_current_user

admin_bp = Blueprint("admin", __name__)


# ---------------------------------------------------------------------------
# Public: flagging a gig or user (POST /api/reports)
# ---------------------------------------------------------------------------


class ReportCreateSchema(Schema):
    reason = fields.Str(required=True, validate=validate.Length(min=3, max=255))
    reported_gig_id = fields.Int(required=False, allow_none=True)
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

    if not data.get("reported_gig_id") and not data.get("reported_user_id"):
        return (
            jsonify(
                {
                    "error": "validation_error",
                    "message": {"reported_gig_id": ["Report must target a gig, a user, or both."]},
                }
            ),
            422,
        )

    if data.get("reported_gig_id") and db.session.get(Gig, data["reported_gig_id"]) is None:
        return jsonify({"error": "not_found", "message": "Reported gig not found."}), 404
    if data.get("reported_user_id") and db.session.get(User, data["reported_user_id"]) is None:
        return jsonify({"error": "not_found", "message": "Reported user not found."}), 404

    report = Report(
        reporter_id=current_user.id,
        reported_gig_id=data.get("reported_gig_id"),
        reported_user_id=data.get("reported_user_id"),
        reason=data["reason"],
    )
    db.session.add(report)
    db.session.commit()

    return jsonify({"report": report.to_dict()}), 201


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

    # Phase 9: an auto-generated moderation report carries a real
    # consequence for the underlying gig, not just a status change on
    # the report itself — DISMISSED means the flag was a false
    # positive (publish it), REVIEWED means the flag was correct
    # (kill it). Manually-filed reports never do this automatically;
    # an admin resolving a user's abuse report doesn't imply any
    # particular action on the gig.
    if report.auto_generated and report.reported_gig_id:
        gig = db.session.get(Gig, report.reported_gig_id)
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
# Admin-only: dispute resolution queue (Phase 6)
# ---------------------------------------------------------------------------


@admin_bp.get("/admin/disputes")
@admin_required
def list_disputes():
    gigs = (
        Gig.query.filter_by(status=GigStatus.DISPUTED)
        .order_by(Gig.created_at.asc())
        .all()
    )
    return jsonify({"gigs": [g.to_dict() for g in gigs]}), 200


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

    return jsonify({"gig": gig.to_dict()}), 200
