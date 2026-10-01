"""Applications blueprint.

Applying itself is an opportunity-scoped action (POST /api/opportunities/:id/applications
— see opportunities/routes.py) since it's created in the context of one opportunity.
This blueprint owns the applicant-side and employer-side actions on an
*existing* application: accept/reject (PATCH /api/applications/:id, per the API
surface table) and a "my applications" listing.
"""

from datetime import datetime, timezone

from flask import Blueprint, current_app, jsonify, request
from marshmallow import Schema, ValidationError, fields, validate

from app.extensions import db, limiter
from app.models.application import Application, ApplicationStatus
from app.models.opportunity import Gig, GigStatus
from app.services import whatsapp_service
from app.services.notification_service import send_critical_email
from app.utils.decorators import load_current_user

applications_bp = Blueprint("applications", __name__)


class ApplicationStatusUpdateSchema(Schema):
    status = fields.Str(
        required=True,
        validate=validate.OneOf([s.value for s in ApplicationStatus if s.value in (
            ApplicationStatus.VIEWED.value, ApplicationStatus.SHORTLISTED.value,
            ApplicationStatus.ACCEPTED.value, ApplicationStatus.REJECTED.value,
            ApplicationStatus.COMPLETED.value,
        )]),
    )


application_status_update_schema = ApplicationStatusUpdateSchema()


@applications_bp.get("/mine")
@load_current_user
def list_my_applications(current_user):
    applications = (
        Application.query.filter_by(applicant_id=current_user.id)
        .order_by(Application.created_at.desc())
        .all()
    )
    return jsonify({"applications": [a.to_dict(include_opportunity=True) for a in applications]}), 200


@applications_bp.patch("/<int:application_id>")
@limiter.limit("30 per hour")
@load_current_user
def update_application_status(current_user, application_id: int):
    """Employer updates an application status (viewed, shortlist, accept, reject, complete)."""
    application = Application.query.get_or_404(application_id)
    gig = application.opportunity

    if gig.employer_id != current_user.id:
        return jsonify({"error": "forbidden", "message": "Only the opportunity owner can update applications."}), 403

    if application.status not in (ApplicationStatus.SUBMITTED, ApplicationStatus.VIEWED, ApplicationStatus.SHORTLISTED):
        return jsonify({"error": "conflict", "message": "This application has already been decided."}), 409

    try:
        data = application_status_update_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({"error": "validation_error", "message": err.messages}), 422

    new_status = ApplicationStatus(data["status"])

    if new_status == ApplicationStatus.ACCEPTED and gig.is_full():
        return jsonify({"error": "conflict", "message": "All positions on this opportunity are already filled."}), 409

    application.status = new_status
    if new_status == ApplicationStatus.VIEWED:
        application.viewed_at = datetime.now(timezone.utc)
    elif new_status == ApplicationStatus.SHORTLISTED:
        application.shortlisted_at = datetime.now(timezone.utc)
    elif new_status == ApplicationStatus.ACCEPTED:
        application.accepted_at = datetime.now(timezone.utc)
        gig.positions_filled += 1
        gig.slots_filled += 1
        if gig.is_full():
            gig.status = GigStatus.IN_PROGRESS
        db.session.add(gig)
    elif new_status == ApplicationStatus.REJECTED:
        application.rejected_at = datetime.now(timezone.utc)
    elif new_status == ApplicationStatus.COMPLETED:
        application.completed_at = datetime.now(timezone.utc)

    db.session.add(application)
    db.session.commit()

    gig_dict = gig.to_dict()
    return jsonify({"application": application.to_dict(), "opportunity": gig_dict, "gig": gig_dict}), 200