"""Gigs blueprint — the feed (PRD §5.2), gig CRUD, and the gig-scoped
actions: applying, completing (Phase 6: two-sided + disputes), and
listing applicants.

Extended for Phase 12: standardized delivery (price_type, deadline,
deliverables).
"""

from datetime import datetime, timezone

from flask import Blueprint, current_app, jsonify, request
from marshmallow import ValidationError
from sqlalchemy import case

from app.blueprints.gigs.schemas import (
    ApplicationCreateSchema,
    DisputeCreateSchema,
    GigCreateSchema,
    GigUpdateSchema,
)
from app.extensions import db, limiter
from app.models.application import Application, ApplicationStatus
from app.models.gig import Gig, GigStatus, GigType, PriceType
from app.models.report import Report
from app.services.dispute_service import (
    DisputeError,
    dispute_completion,
    get_accepted_applicant_ids,
    maybe_auto_complete,
    request_or_confirm_completion,
)
from app.services import whatsapp_service
from app.utils.decorators import load_current_user
from app.utils.moderation import screen_gig_content

gigs_bp = Blueprint("gigs", __name__)

gig_create_schema = GigCreateSchema()
gig_update_schema = GigUpdateSchema()
application_create_schema = ApplicationCreateSchema()
dispute_create_schema = DisputeCreateSchema()


@gigs_bp.get("")
def list_gigs():
    """Filtered, paginated feed, boosted-first (PRD §5.2 / API table:
    GET /api/gigs?campus=&category=&urgent=). Phase 8 adds a `near`
    landmark filter; Phase 9 excludes gigs pending moderation review.

    All filters are applied via SQLAlchemy's parameter-bound query
    API — never raw string interpolation — closing PRD §12 finding #1
    (the f-string SQL injection hole in the original draft).
    """
    query = Gig.query.filter(
        Gig.status == GigStatus.OPEN, Gig.flagged_for_review.is_(False)
    )

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

    price_type = request.args.get("price_type")
    if price_type and price_type in {p.value for p in PriceType}:
        query = query.filter(Gig.price_type == PriceType(price_type))

    min_budget = request.args.get("min_budget", type=float)
    if min_budget is not None:
        query = query.filter(Gig.budget >= min_budget)

    max_budget = request.args.get("max_budget", type=float)
    if max_budget is not None:
        query = query.filter(Gig.budget <= max_budget)

    near = request.args.get("near")
    if near:
        query = query.filter(Gig.landmark.ilike(f"%{near}%"))

    now = datetime.now(timezone.utc)
    is_boost_live = (Gig.is_boosted.is_(True)) & (Gig.boost_expires_at > now)

    # Boosted-first, newest within each tier.
    query = query.order_by(case((is_boost_live, 0), else_=1), Gig.created_at.desc())

    page = request.args.get("page", default=1, type=int)
    if page < 1 or page > 10_000:
        return jsonify({"error": "validation_error", "message": {"page": ["Page must be between 1 and 10000."]}}), 422
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
@limiter.limit("20 per hour")
@load_current_user
def create_gig(current_user):
    try:
        data = gig_create_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({"error": "validation_error", "message": err.messages}), 422

    flag_reason = screen_gig_content(data["title"], data["description"])

    gig = Gig(
        poster_id=current_user.id,
        title=data["title"],
        description=data["description"],
        budget=data["budget"],
        price_type=PriceType(data.get("price_type", "FIXED")),
        gig_type=GigType(data["gig_type"]),
        category=data["category"],
        campus_location=data["campus_location"],
        landmark=data.get("landmark"),
        is_urgent=data.get("is_urgent", False),
        slots_needed=data.get("slots_needed", 1),
        deliverables=",".join(data.get("deliverables") or []) or None,
        flagged_for_review=flag_reason is not None,
        flag_reason=flag_reason,
    )
    if data.get("deadline"):
        gig.deadline = data["deadline"]
    db.session.add(gig)
    db.session.commit()

    if flag_reason:
        # Route to the existing admin reports queue rather than a
        # separate "flagged gigs" screen — one queue, one review
        # habit for the admin to maintain (Phase 9 roadmap item).
        auto_report = Report(
            reporter_id=current_user.id,
            reported_gig_id=gig.id,
            reason=flag_reason,
            auto_generated=True,
        )
        db.session.add(auto_report)
        db.session.commit()

    response = {"gig": gig.to_dict()}
    if flag_reason:
        response["message"] = (
            "Your gig was submitted for a quick review before it goes live "
            "on the feed — this usually takes a few hours."
        )
    return jsonify(response), 201


@gigs_bp.get("/mine")
@load_current_user
def list_my_gigs(current_user):
    """Gigs the current user has posted — the applicant-side mirror of
    GET /api/applications/mine. Not in the original PRD API table but
    needed for a real dashboard, so it follows the same shape/pattern
    as the rest of this blueprint."""
    gigs = (
        Gig.query.filter_by(poster_id=current_user.id)
        .order_by(Gig.created_at.desc())
        .all()
    )
    return jsonify({"gigs": [g.to_dict(include_poster=False) for g in gigs]}), 200


@gigs_bp.get("/<int:gig_id>")
def get_gig(gig_id: int):
    gig = Gig.query.get_or_404(gig_id)
    maybe_auto_complete(gig)
    return jsonify({"gig": gig.to_dict()}), 200


@gigs_bp.post("/<int:gig_id>/applications")
@limiter.limit("20 per hour")
@load_current_user
def apply_to_gig(current_user, gig_id: int):
    gig = Gig.query.get_or_404(gig_id)

    if gig.poster_id == current_user.id:
        return jsonify({"error": "forbidden", "message": "You can't apply to your own gig."}), 403

    if gig.status != GigStatus.OPEN or gig.is_full():
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
@limiter.limit("20 per hour")
@load_current_user
def complete_gig(current_user, gig_id: int):
    """Two-sided completion (Phase 6): the first party's call moves
    the gig to PENDING_CONFIRMATION; the second party's call finalizes
    it. See services/dispute_service.py for the full state machine.
    """
    gig = Gig.query.get_or_404(gig_id)

    try:
        result = request_or_confirm_completion(gig, current_user.id)
    except DisputeError as err:
        return jsonify({"error": "conflict", "message": err.message}), err.status_code

    accepted_ids = get_accepted_applicant_ids(gig)
    is_poster = gig.poster_id == current_user.id
    counterparty_id = next((uid for uid in accepted_ids if uid != current_user.id), None) \
        if not is_poster else (accepted_ids[0] if accepted_ids else None)

    if result["finalized"]:
        # Both sides have confirmed — let everyone involved know via
        # WhatsApp (Phase 7), not just the computed-on-read in-app feed.
        participants = [gig.poster] + [
            a.applicant
            for a in Application.query.filter(
                Application.gig_id == gig.id, Application.applicant_id.in_(accepted_ids)
            )
        ]
        for participant in participants:
            whatsapp_service.notify_gig_completed(
                current_app.config,
                to_phone=participant.phone_number,
                gig_title=gig.title,
                logger=current_app.logger,
            )

    return (
        jsonify(
            {
                "gig": gig.to_dict(),
                "needs_review": result["finalized"],
                "awaiting_confirmation_from": result["awaiting"],
                "counterparty_id": counterparty_id if is_poster else gig.poster_id,
            }
        ),
        200,
    )


@gigs_bp.post("/<int:gig_id>/dispute")
@limiter.limit("5 per hour")
@load_current_user
def dispute_gig(current_user, gig_id: int):
    """Phase 6: the party who hasn't confirmed completion can dispute
    instead, within the confirmation window — routes to the admin
    disputes queue instead of silently auto-completing."""
    gig = Gig.query.get_or_404(gig_id)
    maybe_auto_complete(gig)

    try:
        data = dispute_create_schema.load(request.get_json(silent=True) or {})
        dispute_completion(gig, current_user.id, data["reason"])
    except ValidationError as err:
        return jsonify({"error": "validation_error", "message": err.messages}), 422
    except DisputeError as err:
        return jsonify({"error": "conflict", "message": err.message}), err.status_code
    return jsonify({"gig": gig.to_dict()}), 200
@gigs_bp.patch("/<int:gig_id>")
@limiter.limit("20 per hour")
@load_current_user
def update_gig(current_user, gig_id: int):
    """Update a gig's details — title, description, budget, price
    type, category, urgency, deadline, deliverables."""
    gig = Gig.query.get_or_404(gig_id)
    if gig.poster_id != current_user.id:
        return jsonify({"error": "forbidden", "message": "Only the gig poster can edit this gig."}), 403

    try:
        data = gig_update_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({"error": "validation_error", "message": err.messages}), 422

    for field in (
        "title",
        "description",
        "budget",
        "category",
        "is_urgent",
        "landmark",
    ):
        if field in data:
            setattr(gig, field, data[field])

    if "price_type" in data:
        gig.price_type = PriceType(data["price_type"])
    if "deadline" in data:
        gig.deadline = data.get("deadline")
    if "deliverables" in data:
        gig.deliverables = ",".join(data["deliverables"]) if data["deliverables"] else None

    db.session.add(gig)
    db.session.commit()

    return jsonify({"gig": gig.to_dict()}), 200
