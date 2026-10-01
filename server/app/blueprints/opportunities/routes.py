"""Opportunities blueprint — the marketplace feed, opportunity CRUD, and
opportunity-scoped actions: applying, completing, and listing applicants.

Follows PRD §5.2: filtered, paginated feed; clear verification labels;
two-sided completion; dispute resolution.
"""

from datetime import datetime, timezone

from flask import Blueprint, current_app, jsonify, request
from marshmallow import ValidationError
from sqlalchemy import case

from app.blueprints.opportunities.schemas import (
    ApplicationCreateSchema,
    ApplicationStatusUpdateSchema,
    OpportunityCreateSchema,
    OpportunityUpdateSchema,
)
from app.extensions import db, limiter
from app.models.application import Application, ApplicationStatus
from app.models.opportunity import Gig, GigStatus, GigType, PriceType, OpportunityType, CompensationType, WorkArrangement
from app.models.report import Report
from app.services.dispute_service import (
    DisputeError,
    dispute_completion,
    get_accepted_applicant_ids,
    maybe_auto_complete,
    request_or_confirm_completion,
)
from app.services import whatsapp_service
from app.utils.decorators import load_current_user, admin_required
from app.utils.moderation import screen_gig_content

opportunities_bp = Blueprint("opportunities", __name__)

opportunity_create_schema = OpportunityCreateSchema()
opportunity_update_schema = OpportunityUpdateSchema()
application_create_schema = ApplicationCreateSchema()
application_status_update_schema = ApplicationStatusUpdateSchema()


@opportunities_bp.get("")
def list_opportunities():
    """Filtered, paginated feed, featured-first (PRD §5.2)."""
    query = Gig.query.filter(
        Gig.status == GigStatus.OPEN, Gig.flagged_for_review.is_(False)
    )

    campus = request.args.get("campus")
    if campus:
        query = query.filter(Gig.campus_location == campus)

    category = request.args.get("category")
    if category:
        query = query.filter(Gig.category == category)

    gig_type = request.args.get("type")
    if gig_type and gig_type in {t.value for t in GigType}:
        query = query.filter(Gig.gig_type == GigType(gig_type))

    opportunity_type = request.args.get("opportunity_type")
    if opportunity_type:
        query = query.filter(Gig.opportunity_type == opportunity_type)

    price_type = request.args.get("price_type")
    if price_type and price_type in {p.value for p in PriceType}:
        query = query.filter(Gig.price_type == PriceType(price_type))

    min_budget = request.args.get("min_budget", type=float)
    if min_budget is not None:
        query = query.filter(Gig.budget >= min_budget)

    max_budget = request.args.get("max_budget", type=float)
    if max_budget is not None:
        query = query.filter(Gig.budget <= max_budget)

    compensation_type = request.args.get("compensation_type")
    if compensation_type:
        query = query.filter(Gig.compensation_type == compensation_type)

    work_arrangement = request.args.get("work_arrangement")
    if work_arrangement:
        query = query.filter(Gig.work_arrangement == work_arrangement)

    near = request.args.get("near")
    if near:
        query = query.filter(Gig.landmark.ilike(f"%{near}%"))

    now = datetime.now(timezone.utc)
    is_featured_live = (Gig.is_featured.is_(True)) & (Gig.featured_expires_at > now)

    query = query.order_by(
        case((is_featured_live, 0), else_=1),
        Gig.created_at.desc()
    )

    page = request.args.get("page", default=1, type=int)
    if page < 1 or page > 10_000:
        return jsonify({"error": "validation_error", "message": {"page": ["Page must be between 1 and 10000."]}}), 422
    per_page = current_app.config["GIGS_PER_PAGE"]
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return (
        jsonify(
            {
                "opportunities": [g.to_dict() for g in pagination.items],
                "gigs": [g.to_dict() for g in pagination.items],
                "page": pagination.page,
                "per_page": per_page,
                "total": pagination.total,
                "total_pages": pagination.pages,
            }
        ),
        200,
    )


@opportunities_bp.post("")
@limiter.limit("20 per hour")
@load_current_user
def create_opportunity(current_user):
    """Create a new opportunity. Employers must be verified first."""
    if current_user.user_type == "EMPLOYER" and not current_user.is_verified_employer:
        return jsonify({"error": "forbidden", "message": "You must be a verified employer to post opportunities."}), 403

    try:
        data = opportunity_create_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({"error": "validation_error", "message": err.messages}), 422

    flag_reason = screen_gig_content(data["title"], data["description"])

    # Support both new opportunity_type and legacy gig_type
    opp_type = data.get("opportunity_type") or data.get("gig_type")
    if opp_type:
        try:
            opp_type = OpportunityType(opp_type)
        except ValueError:
            opp_type = None

    budget = data.get("budget")
    if budget is None and data.get("pay_max"):
        budget = data["pay_max"]

    gig = Gig(
        employer_id=current_user.id,
        poster_id=current_user.id,
        title=data["title"],
        description=data["description"],
        requirements=data.get("requirements"),
        responsibilities=data.get("responsibilities"),
        opportunity_type=opp_type,
        category=data["category"],
        skills_required=",".join(data.get("skills_required") or []),
        compensation_type=CompensationType(data.get("compensation_type", CompensationType.NEGOTIABLE.value)),
        pay_min=data.get("pay_min") or budget,
        pay_max=data.get("pay_max") or budget,
        pay_period=data.get("pay_period", "per_task"),
        work_arrangement=WorkArrangement(data.get("work_arrangement", WorkArrangement.ON_SITE.value)),
        location=data.get("location"),
        campus_location=data["campus_location"],
        landmark=data.get("landmark"),
        budget=budget,
        price_type=PriceType(data.get("price_type", PriceType.FIXED.value)),
        is_urgent=data.get("is_urgent", False),
        positions_available=data.get("positions_available") or data.get("slots_needed") or 1,
        slots_needed=data.get("positions_available") or data.get("slots_needed") or 1,
        deadline=data.get("deadline"),
        start_date=data.get("start_date"),
        end_date=data.get("end_date"),
        duration_weeks=data.get("duration_weeks"),
        deliverables=",".join(data.get("deliverables") or []) if data.get("deliverables") else None,
        flagged_for_review=flag_reason is not None,
        flag_reason=flag_reason,
        status=GigStatus.OPEN,
    )

    gig.published_at = datetime.now(timezone.utc)

    db.session.add(gig)
    db.session.commit()

    if flag_reason:
        auto_report = Report(
            reporter_id=current_user.id,
            reported_opportunity_id=gig.id,
            reason=flag_reason,
            auto_generated=True,
        )
        db.session.add(auto_report)
        db.session.commit()

    response = {"opportunity": gig.to_dict(), "gig": gig.to_dict()}
    if flag_reason:
        response["message"] = (
            "Your opportunity was submitted for review before going live "
            "on the marketplace — this usually takes a few hours."
        )
    return jsonify(response), 201


@opportunities_bp.get("/mine")
@load_current_user
def list_my_opportunities(current_user):
    """Opportunities the current user has posted."""
    gigs = (
        Gig.query.filter_by(employer_id=current_user.id)
        .order_by(Gig.created_at.desc())
        .all()
    )
    gig_list = [g.to_dict(include_employer=False) for g in gigs]
    return jsonify({"opportunities": gig_list, "gigs": gig_list}), 200


@opportunities_bp.get("/<int:gig_id>")
def get_opportunity(gig_id: int):
    gig = Gig.query.get_or_404(gig_id)
    maybe_auto_complete(gig)
    gig_dict = gig.to_dict()
    return jsonify({"opportunity": gig_dict, "gig": gig_dict}), 200


@opportunities_bp.post("/<int:gig_id>/applications")
@limiter.limit("20 per hour")
@load_current_user
def apply_to_opportunity(current_user, gig_id: int):
    gig = Gig.query.get_or_404(gig_id)

    if gig.employer_id == current_user.id:
        return jsonify({"error": "forbidden", "message": "You can't apply to your own opportunity."}), 403

    if gig.status != GigStatus.OPEN or gig.is_full():
        return jsonify({"error": "conflict", "message": "This opportunity is no longer open."}), 409

    try:
        data = application_create_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({"error": "validation_error", "message": err.messages}), 422

    existing = Application.query.filter_by(
        opportunity_id=gig.id, applicant_id=current_user.id
    ).first()
    if existing is not None:
        return jsonify({"error": "conflict", "message": "You already applied to this opportunity."}), 409

    application = Application(
        opportunity_id=gig.id,
        applicant_id=current_user.id,
        proposal_text=data.get("proposal_text"),
        portfolio_url=data.get("portfolio_url"),
    )
    db.session.add(application)
    db.session.commit()

    return jsonify({"application": application.to_dict()}), 201


@opportunities_bp.get("/<int:gig_id>/applications")
@load_current_user
def list_opportunity_applications(current_user, gig_id: int):
    gig = Gig.query.get_or_404(gig_id)
    if gig.employer_id != current_user.id:
        return jsonify({"error": "forbidden", "message": "Only the owner can view applicants."}), 403

    applications = (
        Application.query.filter_by(opportunity_id=gig.id)
        .order_by(Application.created_at.desc())
        .all()
    )
    return jsonify({"applications": [a.to_dict() for a in applications]}), 200


@opportunities_bp.post("/<int:gig_id>/complete")
@limiter.limit("20 per hour")
@load_current_user
def complete_opportunity(current_user, gig_id: int):
    gig = Gig.query.get_or_404(gig_id)

    try:
        result = request_or_confirm_completion(gig, current_user.id)
    except DisputeError as err:
        return jsonify({"error": "conflict", "message": err.message}), err.status_code

    accepted_ids = get_accepted_applicant_ids(gig)
    is_poster = gig.employer_id == current_user.id
    counterparty_id = next((uid for uid in accepted_ids if uid != current_user.id), None) \
        if not is_poster else (accepted_ids[0] if accepted_ids else None)

    if result["finalized"]:
        participants = [gig.poster] + [
            a.applicant
            for a in Application.query.filter(
                Application.opportunity_id == gig.id, Application.applicant_id.in_(accepted_ids)
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
                "opportunity": gig.to_dict(),
                "gig": gig.to_dict(),
                "needs_review": result["finalized"],
                "awaiting_confirmation_from": result["awaiting"],
                "counterparty_id": counterparty_id if is_poster else gig.employer_id,
            }
        ),
        200,
    )


@opportunities_bp.post("/<int:gig_id>/dispute")
@limiter.limit("5 per hour")
@load_current_user
def dispute_opportunity(current_user, gig_id: int):
    gig = Gig.query.get_or_404(gig_id)
    maybe_auto_complete(gig)

    data = request.get_json(silent=True) or {}
    reason = data.get("reason", "")

    try:
        dispute_completion(gig, current_user.id, reason)
    except DisputeError as err:
        return jsonify({"error": "conflict", "message": err.message}), err.status_code
    gig_dict = gig.to_dict()
    return jsonify({"opportunity": gig_dict, "gig": gig_dict}), 200


@opportunities_bp.patch("/<int:gig_id>")
@limiter.limit("20 per hour")
@load_current_user
def update_opportunity(current_user, gig_id: int):
    gig = Gig.query.get_or_404(gig_id)
    if gig.employer_id != current_user.id:
        return jsonify({"error": "forbidden", "message": "Only the owner can edit this opportunity."}), 403

    try:
        data = opportunity_update_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({"error": "validation_error", "message": err.messages}), 422

    for field in (
        "title", "description", "category", "is_urgent", "landmark",
    ):
        if field in data:
            setattr(gig, field, data[field])

    if "budget" in data:
        gig.budget = data["budget"]
        gig.pay_max = data["budget"]
    if "price_type" in data:
        gig.price_type = PriceType(data["price_type"])
    if "deadline" in data:
        gig.deadline = data.get("deadline")
    if "deliverables" in data:
        gig.deliverables = ",".join(data["deliverables"]) if data["deliverables"] else None
    if "compensation_type" in data:
        gig.compensation_type = data["compensation_type"]
    if "pay_min" in data:
        gig.pay_min = data["pay_min"]
    if "pay_max" in data:
        gig.pay_max = data["pay_max"]

    db.session.add(gig)
    db.session.commit()

    gig_dict = gig.to_dict()
    return jsonify({"opportunity": gig_dict, "gig": gig_dict}), 200


@opportunities_bp.delete("/<int:gig_id>")
@limiter.limit("10 per hour")
@load_current_user
def delete_opportunity(current_user, gig_id: int):
    gig = Gig.query.get_or_404(gig_id)
    if gig.employer_id != current_user.id:
        return jsonify({"error": "forbidden", "message": "Only the owner can delete this opportunity."}), 403

    if gig.status not in (GigStatus.DRAFT, GigStatus.OPEN, GigStatus.PENDING_REVIEW):
        return jsonify({"error": "conflict", "message": "This opportunity can't be deleted in its current state."}), 409

    db.session.delete(gig)
    db.session.commit()

    return jsonify({"message": "Opportunity deleted."}), 200