"""Applications blueprint.

Applying itself is a gig-scoped action (POST /api/gigs/:id/applications
— see gigs/routes.py) since it's created in the context of one gig.
This blueprint owns the applicant-side and poster-side actions on an
*existing* application: accept/reject (PATCH /api/applications/:id,
per the API surface table) and a "my applications" listing.
"""

from flask import Blueprint, current_app, jsonify, request
from marshmallow import Schema, ValidationError, fields, validate

from app.extensions import db
from app.models.application import Application, ApplicationStatus
from app.models.gig import Gig, GigStatus
from app.services.notification_service import send_critical_email
from app.utils.decorators import load_current_user

applications_bp = Blueprint("applications", __name__)


class ApplicationStatusUpdateSchema(Schema):
    status = fields.Str(
        required=True,
        validate=validate.OneOf([ApplicationStatus.ACCEPTED.value, ApplicationStatus.REJECTED.value]),
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
    return jsonify({"applications": [a.to_dict() for a in applications]}), 200


@applications_bp.patch("/<int:application_id>")
@load_current_user
def update_application_status(current_user, application_id: int):
    """Poster accepts or rejects an applicant. Accepting one applicant
    moves the gig to IN_PROGRESS (PRD §5.2); accepting also auto-
    rejects the other pending applicants so only one accepted
    application ever exists per gig."""
    application = Application.query.get_or_404(application_id)
    gig = application.gig

    if gig.poster_id != current_user.id:
        return jsonify({"error": "forbidden", "message": "Only the gig poster can accept or reject applicants."}), 403

    if application.status != ApplicationStatus.PENDING:
        return jsonify({"error": "conflict", "message": "This application has already been decided."}), 409

    try:
        data = application_status_update_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({"error": "validation_error", "message": err.messages}), 422

    new_status = ApplicationStatus(data["status"])
    application.status = new_status

    if new_status == ApplicationStatus.ACCEPTED:
        gig.status = GigStatus.IN_PROGRESS
        db.session.add(gig)

        other_pending = Application.query.filter(
            Application.gig_id == gig.id,
            Application.id != application.id,
            Application.status == ApplicationStatus.PENDING,
        ).all()
        for other in other_pending:
            other.status = ApplicationStatus.REJECTED
            db.session.add(other)

    db.session.commit()

    if new_status == ApplicationStatus.ACCEPTED:
        send_critical_email(
            current_app.config,
            application.applicant.email,
            subject=f'Your application for "{gig.title}" was accepted',
            body=(
                f"Hi {application.applicant.name},\n\n"
                f'Good news — {gig.poster.name} accepted your application for "{gig.title}".\n'
                "Open Soko Comrada to coordinate next steps."
            ),
            logger=current_app.logger,
        )

    return jsonify({"application": application.to_dict(), "gig": gig.to_dict()}), 200
