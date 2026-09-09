
import smtplib
from dataclasses import dataclass
from datetime import datetime, timezone
from email.message import EmailMessage

from app.models.application import Application, ApplicationStatus
from app.models.gig import Gig, GigStatus
from app.models.review import Review


@dataclass
class NotificationItem:
    type: str
    message: str
    created_at: datetime
    gig_id: int | None = None

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "message": self.message,
            "created_at": self.created_at.isoformat(),
            "gig_id": self.gig_id,
        }


def get_notifications_for_user(user_id: int, limit: int = 20) -> list[dict]:
    items: list[NotificationItem] = []

    # New applications on gigs this user posted.
    my_gig_ids_subq = Gig.query.with_entities(Gig.id).filter(Gig.poster_id == user_id)
    my_gig_ids = [row[0] for row in my_gig_ids_subq]

    if my_gig_ids:
        incoming = (
            Application.query.filter(Application.gig_id.in_(my_gig_ids))
            .order_by(Application.created_at.desc())
            .limit(limit)
            .all()
        )
        for app_ in incoming:
            items.append(
                NotificationItem(
                    type="new_application",
                    message=f'{app_.applicant.name} applied to your gig "{app_.gig.title}".',
                    created_at=app_.created_at,
                    gig_id=app_.gig_id,
                )
            )

    # Status changes on applications this user submitted.
    mine = (
        Application.query.filter(
            Application.applicant_id == user_id,
            Application.status != ApplicationStatus.PENDING,
        )
        .order_by(Application.created_at.desc())
        .limit(limit)
        .all()
    )
    for app_ in mine:
        verb = "accepted" if app_.status == ApplicationStatus.ACCEPTED else "rejected"
        items.append(
            NotificationItem(
                type=f"application_{verb}",
                message=f'Your application for "{app_.gig.title}" was {verb}.',
                created_at=app_.created_at,
                gig_id=app_.gig_id,
            )
        )

    # Gigs the user posted that are now completed.
    completed = (
        Gig.query.filter(Gig.poster_id == user_id, Gig.status == GigStatus.COMPLETED)
        .order_by(Gig.created_at.desc())
        .limit(limit)
        .all()
    )
    for gig in completed:
        items.append(
            NotificationItem(
                type="gig_completed",
                message=f'Your gig "{gig.title}" was marked completed.',
                created_at=gig.created_at,
                gig_id=gig.id,
            )
        )

    # Reviews received.
    reviews = (
        Review.query.filter(Review.reviewee_id == user_id)
        .order_by(Review.created_at.desc())
        .limit(limit)
        .all()
    )
    for review in reviews:
        items.append(
            NotificationItem(
                type="review_received",
                message=f"You received a {review.rating}-star review.",
                created_at=review.created_at,
                gig_id=review.gig_id,
            )
        )

    items.sort(key=lambda i: i.created_at, reverse=True)
    return [i.to_dict() for i in items[:limit]]


def send_critical_email(app_config, to_email: str, subject: str, body: str, logger=None) -> bool:
    """Best-effort email fallback for critical actions (PRD §5.5).

    Returns True if a send was attempted successfully, False if it
    was only logged (no SMTP configured) or failed. Never raises —
    a notification failure must not fail the request that triggered
    it (e.g. accepting an application should still succeed even if
    the email bounces).
    """
    host = app_config.get("SMTP_HOST")
    if not host:
        if logger:
            logger.info("SMTP not configured — would send email to %s: %s", to_email, subject)
        return False

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = app_config.get("SMTP_FROM_ADDRESS")
    message["To"] = to_email
    message.set_content(body)

    try:
        with smtplib.SMTP(host, app_config.get("SMTP_PORT", 587), timeout=10) as smtp:
            if app_config.get("SMTP_USE_TLS", True):
                smtp.starttls()
            username = app_config.get("SMTP_USERNAME")
            password = app_config.get("SMTP_PASSWORD")
            if username and password:
                smtp.login(username, password)
            smtp.send_message(message)
        return True
    except (smtplib.SMTPException, OSError):
        if logger:
            logger.exception("Failed to send critical email to %s", to_email)
        return False
