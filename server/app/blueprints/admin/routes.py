
from flask import Blueprint, jsonify, request
from marshmallow import Schema, ValidationError, fields, validate

from app.extensions import db
from app.models.gig import Gig
from app.models.payment import Payment, PaymentStatus
from app.models.report import Report, ReportStatus
from app.models.user import User
from app.services.payment_service import verify_payment
from app.utils.decorators import admin_required, load_current_user

admin_bp = Blueprint("admin", __name__)


# --------------------------------------------------------
# Public: flagging a gig or user (POST /api/reports)
# -------------------------------------------------------


class ReportCreateSchema(Schema):
    reason = fields.Str(required=True, validate=validate.Length(min=3, max=255))
    reported_gig_id = fields.Int(required=False, allow_none=True)
    reported_user_id = fields.Int(required=False, allow_none=True)


report_create_schema = ReportCreateSchema()


@admin_bp.post("/reports")
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


# --------------------------------------------------
# Admin-only: payment verification queue
# --------------------------------------------------------


@admin_bp.get("/admin/payments/pending")
@admin_required
def list_pending_payments():
    payments = (
        Payment.query.filter_by(status=PaymentStatus.PENDING)
        .order_by(Payment.created_at.asc())
        .all()
    )
    return jsonify({"payments": [p.to_dict(include_mpesa_code=True) for p in payments]}), 200


class PaymentDecisionSchema(Schema):
    approve = fields.Bool(required=True)


payment_decision_schema = PaymentDecisionSchema()


@admin_bp.post("/admin/payments/<int:payment_id>/decision")
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


# -----------------------------------------------
# Admin-only: reports queue
# -----------------------------------------------------


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
@admin_required
def resolve_report(report_id: int):
    report = Report.query.get_or_404(report_id)

    try:
        data = report_resolution_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({"error": "validation_error", "message": err.messages}), 422

    report.status = ReportStatus(data["status"])
    db.session.commit()

    return jsonify({"report": report.to_dict()}), 200
