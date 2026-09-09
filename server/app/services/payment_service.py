from datetime import datetime, timedelta, timezone

from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.gig import Gig
from app.models.payment import Payment, PaymentPurpose, PaymentStatus
from app.models.user import User
from app.utils.validators import normalize_mpesa_code, validate_mpesa_code

BOOST_DURATION_HOURS = 24
SUBSCRIPTION_DURATION_DAYS = 7


class PaymentError(Exception):
    """bad code format, duploicate code, unknown gig, etc"""
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

    


def fee_for_purpose(app_config, purpose: PaymentPurpose) -> float:
    if purpose == PaymentPurpose.BOOST:
        return float(app_config["BOOST_FEE_KES"])
    if purpose == PaymentPurpose.SUBSCRIPTION:
        return float(app_config["SUBSCRIPTION_FEE_KES"])
    raise PaymentError(f"No configured fee for purpose {purpose.value}.")


def submit_payment(
    *,
    app_config,
    user: User,
    mpesa_code: str,
    purpose: PaymentPurpose,
    gig: Gig | None = None,
) -> Payment:
    if not validate_mpesa_code(mpesa_code):
        raise PaymentError(
            "That doesn't look like a valid M-Pesa confirmation code."
        )
    code = normalize_mpesa_code(mpesa_code)

    if purpose == PaymentPurpose.BOOST and gig is None:
        raise PaymentError("A gig_id is required to boost a gig.")
    if purpose == PaymentPurpose.BOOST and gig.poster_id != user.id:
        raise PaymentError("You can only boost your own gig.", status_code=403)

    amount = fee_for_purpose(app_config, purpose)

    payment = Payment(
        user_id=user.id,
        gig_id=gig.id if gig else None,
        mpesa_code=code,
        amount=amount,
        purpose=purpose,
        status=PaymentStatus.PENDING,
    )
    db.session.add(payment)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise PaymentError(
            "This M-Pesa code has already been submitted.", status_code=409
        )
    return payment


def apply_verified_payment(payment: Payment) -> None:
    """Side effects of an admin marking a payment VERIFIED: activate
    the boost or extend the subscription. Idempotent-ish — re-running
    it just re-extends the window, which is an acceptable admin-side
    behavior (no destructive effect)."""
    now = datetime.now(timezone.utc)

    if payment.purpose == PaymentPurpose.BOOST and payment.gig is not None:
        payment.gig.is_boosted = True
        payment.gig.boost_expires_at = now + timedelta(hours=BOOST_DURATION_HOURS)
        db.session.add(payment.gig)

    elif payment.purpose == PaymentPurpose.SUBSCRIPTION:
        payment.user.is_verified_entrepreneur = True
        db.session.add(payment.user)

    db.session.commit()


def verify_payment(payment: Payment, approve: bool) -> Payment:
    payment.status = PaymentStatus.VERIFIED if approve else PaymentStatus.REJECTED
    db.session.add(payment)
    db.session.commit()

    if approve:
        apply_verified_payment(payment)

    return payment
