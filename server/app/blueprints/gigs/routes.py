"""Gigs blueprint — the feed (PRD §5.2), gig CRUD, and the two
gig-scoped actions from the API surface table: applying to a gig and
marking it complete.
"""

from datetime import datetime, timezone

from flask import Blueprint, current_app, jsonify, request
from marshmallow import ValidationError
from sqlalchemy import case

from app.blueprints.gigs.schemas import ApplicationCreateSchema, GigCreateSchema
from app.extensions import db
from app.models.application import Application, ApplicationStatus
from app.models.gig import Gig, GigStatus, GigType
from app.utils.decorators import load_current_user

gigs_bp = Blueprint("gigs", __name__)

gig_create_schema = GigCreateSchema()
application_create_schema = ApplicationCreateSchema()


@gigs_bp.get("")
def list_gigs():
    """Filtered, paginated feed, boosted-first (PRD §5.2 / API table:
    GET /api/gigs?campus=&category=&urgent=).

    All filters are applied via SQLAlchemy's parameter-bound query
    API — never raw string interpolation — closing PRD §12 finding #1
    (the f-string SQL injection hole in the original draft).
    """
    query = Gig.query.filter(Gig.status == GigStatus.OPEN)

    campus = request.args.get("campus")
    if campus:
        query = query.filter(Gig.campus_location == campus)

    category = request.args.get("category")
    if category:
        query = query.filter(Gig.category == category)

    urgent = request.args.get("urgent")
    if urgent is not None:
        query = query.filter(Gig.is_urgent == (urgent.lower() in ("1", "true", "yes")))

    gig_type = request.args.get("type")
    if gig_type and gig_type in {t.value for t in GigType}:
        query = query.filter(Gig.gig_type == GigType(gig_type))

    min_budget = request.args.get("min_budget", type=float)
    if min_budget is not None:
        query = query.filter(Gig.budget >= min_budget)

    max_budget = request.args.get("max_budget", type=float)
    if max_budget is not None:
        query = query.filter(Gig.budget <= max_budget)

    now = datetime.now(timezone.utc)
    is_boost_live = (Gig.is_boosted.is_(True)) & (Gig.boost_expires_at > now)

    # Boosted-first, newest within each tier.
    query = query.order_by(case((is_boost_live, 0), else_=1), Gig.created_at.desc())

    page = request.args.get("page", default=1, type=int)
    per_page = current_app.config["GIGS_PER_PAGE"]
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return (
        jsonify(
            {
                "gigs": [g.to_dict() for g in pagination.items],
                "page": pagination.page,
                "per_page": per_page,
                "total": pagination.total,
                "total_pages": pagination.pages,
            }
        ),
        200,
    )


@gigs_bp.post("")
@load_current_user
def create_gig(current_user):
    try:
        data = gig_create_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({"error": "validation_error", "message": err.messages}), 422

    gig = Gig(
        poster_id=current_user.id,
        title=data["title"],
        description=data["description"],
        budget=data["budget"],
        gig_type=GigType(data["gig_type"]),
        category=data["category"],
        campus_location=data["campus_location"],
        is_urgent=data.get("is_urgent", False),
    )
    db.session.add(gig)
    db.session.commit()

    return jsonify({"gig": gig.to_dict()}), 201


@gigs_bp.get("/<int:gig_id>")
def get_gig(gig_id: int):
    gig = Gig.query.get_or_404(gig_id)
    return jsonify({"gig": gig.to_dict()}), 200


@gigs_bp.post("/<int:gig_id>/applications")
@load_current_user
def apply_to_gig(current_user, gig_id: int):
    gig = Gig.query.get_or_404(gig_id)

    if gig.poster_id == current_user.id:
        return jsonify({"error": "forbidden", "message": "You can't apply to your own gig."}), 403

    if gig.status != GigStatus.OPEN:
        return jsonify({"error": "conflict", "message": "This gig is no longer open."}), 409

    try:
        data = application_create_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({"error": "validation_error", "message": err.messages}), 422

    existing = Application.query.filter_by(
        gig_id=gig.id, applicant_id=current_user.id
    ).first()
    if existing is not None:
        return jsonify({"error": "conflict", "message": "You already applied to this gig."}), 409

    application = Application(
        gig_id=gig.id,
        applicant_id=current_user.id,
        proposal_text=data.get("proposal_text"),
    )
    db.session.add(application)
    db.session.commit()

    return jsonify({"application": application.to_dict()}), 201


@gigs_bp.get("/<int:gig_id>/applications")
@load_current_user
def list_gig_applications(current_user, gig_id: int):
    """Poster reviews applicants (PRD §5.2) — only the gig's poster
    may see the applicant list."""
    gig = Gig.query.get_or_404(gig_id)
    if gig.poster_id != current_user.id:
        return jsonify({"error": "forbidden", "message": "Only the gig poster can view applicants."}), 403

    applications = (
        Application.query.filter_by(gig_id=gig.id)
        .order_by(Application.created_at.desc())
        .all()
    )
    return jsonify({"applications": [a.to_dict() for a in applications]}), 200


@gigs_bp.post("/<int:gig_id>/complete")
@load_current_user
def complete_gig(current_user, gig_id: int):
    """Either party marks the gig COMPLETED; triggers review prompt
    (PRD §5.2) — the frontend uses `needs_review` in the response to
    surface that prompt."""
    gig = Gig.query.get_or_404(gig_id)

    accepted_application = Application.query.filter_by(
        gig_id=gig.id, status=ApplicationStatus.ACCEPTED
    ).first()

    is_poster = gig.poster_id == current_user.id
    is_accepted_applicant = (
        accepted_application is not None
        and accepted_application.applicant_id == current_user.id
    )
    if not (is_poster or is_accepted_applicant):
        return (
            jsonify(
                {
                    "error": "forbidden",
                    "message": "Only the poster or the accepted applicant can complete this gig.",
                }
            ),
            403,
        )

    if gig.status not in (GigStatus.OPEN, GigStatus.IN_PROGRESS):
        return jsonify({"error": "conflict", "message": "This gig can't be completed from its current status."}), 409

    gig.status = GigStatus.COMPLETED
    db.session.commit()

    return (
        jsonify(
            {
                "gig": gig.to_dict(),
                "needs_review": True,
                "counterparty_id": (
                    accepted_application.applicant_id if is_poster and accepted_application else gig.poster_id
                ),
            }
        ),
        200,
    )

