"""Two-sided completion and dispute resolution (Phase 6 roadmap item).

Replaces the MVP's "either party marks complete, done" with: first
party requests completion, the other party has CONFIRMATION_WINDOW
(48h, see models/gig.py) to confirm or dispute, and it auto-completes
if they do neither. This closes the PRD §14 open question about who
resolves a one-sided completion claim.
"""

from datetime import datetime, timezone

from app.extensions import db
from app.models.application import Application, ApplicationStatus
from app.models.gig import Gig, GigStatus


class DisputeError(Exception):
    """Raised for expected, user-facing failures in the
    completion/dispute flow. Routes translate these into 4xx JSON
    responses."""

    def __init__(self, message: str, status_code: int = 409):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def get_accepted_applicant_ids(gig: Gig) -> list[int]:
    return [
        a.applicant_id
        for a in Application.query.filter_by(
            gig_id=gig.id, status=ApplicationStatus.ACCEPTED
        ).all()
    ]


def get_role(gig: Gig, user_id: int) -> str | None:
    """Returns 'poster', 'counterparty', or None if the user has no
    standing to act on this gig's completion."""
    if gig.poster_id == user_id:
        return "poster"
    if user_id in get_accepted_applicant_ids(gig):
        return "counterparty"
    return None


def maybe_auto_complete(gig: Gig) -> bool:
    """Lazily finalizes a gig whose confirmation window has lapsed
    with no dispute filed. Called on every read/write path that
    touches a gig, since there's no scheduled-job infra in this
    deployment yet. Returns True if it changed anything."""
    if gig.status != GigStatus.PENDING_CONFIRMATION or gig.disputed:
        return False
    if not gig.is_past_confirmation_deadline():
        return False

    gig.status = GigStatus.COMPLETED
    db.session.add(gig)
    db.session.commit()
    return True


def request_or_confirm_completion(gig: Gig, user_id: int) -> dict:
    """The single entry point for POST /gigs/:id/complete. Returns
    {"finalized": bool, "awaiting": "poster"|"counterparty"|None}.
    """
    maybe_auto_complete(gig)

    role = get_role(gig, user_id)
    if role is None:
        raise DisputeError(
            "Only the poster or an accepted applicant can complete this gig.", 403
        )

    if gig.status == GigStatus.DISPUTED:
        raise DisputeError("This gig is disputed — an admin needs to resolve it first.")
    if gig.status == GigStatus.COMPLETED:
        raise DisputeError("This gig is already completed.")
    if gig.status not in (GigStatus.OPEN, GigStatus.IN_PROGRESS, GigStatus.PENDING_CONFIRMATION):
        raise DisputeError("This gig can't be completed from its current status.")

    already_confirmed = (
        gig.completed_by_poster if role == "poster" else gig.completed_by_counterparty
    )
    if already_confirmed:
        raise DisputeError("You've already confirmed completion — waiting on the other side.")

    if role == "poster":
        gig.completed_by_poster = True
    else:
        gig.completed_by_counterparty = True

    if gig.completed_by_poster and gig.completed_by_counterparty:
        gig.status = GigStatus.COMPLETED
        db.session.add(gig)
        db.session.commit()
        return {"finalized": True, "awaiting": None}

    if gig.status != GigStatus.PENDING_CONFIRMATION:
        gig.status = GigStatus.PENDING_CONFIRMATION
        gig.completion_requested_at = datetime.now(timezone.utc)

    db.session.add(gig)
    db.session.commit()
    awaiting = "counterparty" if role == "poster" else "poster"
    return {"finalized": False, "awaiting": awaiting}


def dispute_completion(gig: Gig, user_id: int, reason: str) -> Gig:
    role = get_role(gig, user_id)
    if role is None:
        raise DisputeError("Only the poster or an accepted applicant can dispute this gig.", 403)
    if gig.status != GigStatus.PENDING_CONFIRMATION:
        raise DisputeError("Only a gig awaiting confirmation can be disputed.")

    gig.disputed = True
    gig.dispute_reason = reason
    gig.disputed_by_id = user_id
    gig.status = GigStatus.DISPUTED
    db.session.add(gig)
    db.session.commit()
    return gig


def resolve_dispute(gig: Gig, resolution: str) -> Gig:
    """Admin action: resolution is 'COMPLETED' or 'CANCELLED'."""
    if gig.status != GigStatus.DISPUTED:
        raise DisputeError("This gig isn't currently disputed.")
    if resolution not in ("COMPLETED", "CANCELLED"):
        raise DisputeError("Resolution must be COMPLETED or CANCELLED.", 400)

    gig.status = GigStatus(resolution)
    gig.disputed = False
    db.session.add(gig)
    db.session.commit()
    return gig