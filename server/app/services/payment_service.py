"""Payment domain logic.

Kept out of the blueprint routes so the payments and admin-approval
flow — the part of this product most likely to need urgent changes
(new fee tiers, a new verification method) — lives in one file, per
PRD §9.

Three verification paths now exist:
  - MANUAL: a student submits an M-Pesa confirmation code, an admin
    cross-checks it against the till statement (original MVP flow —
    kept as the fallback when STK Push isn't configured or a callback
    never arrives).
  - STK_PUSH: Daraja STK Push (Phase 5 roadmap item) — Safaricom's
    callback verifies the payment automatically, no admin touch.
  - CREDIT: a free boost earned via the referral program (Phase 10)
    is redeemed instantly, no M-Pesa involved at all.
"""

from datetime import datetime, timedelta, timezone

from flask import current_app
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.gig import Gig
from app.models.payment import Payment, PaymentMethod, PaymentPurpose, PaymentStatus
from app.models.user import User
from app.utils.validators import normalize_mpesa_code, validate_mpesa_code
from app.services import daraja_service, whatsapp_service

BOOST_DURATION_HOURS = 24
SUBSCRIPTION_DURATION_DAYS = 7


class PaymentError(Exception):
    """Raised for expected, user-facing payment failures (bad code
    format, duplicate code, unknown gig, etc). Routes translate these
    into 4xx JSON responses."""

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


def _validate_boost_target(user: User, purpose: PaymentPurpose, gig: Gig | None) -> None:
    if purpose == PaymentPurpose.BOOST and gig is None:
        raise PaymentError("A gig_id is required to boost a gig.")
    if purpose == PaymentPurpose.BOOST and gig.poster_id != user.id:
        raise PaymentError("You can only boost your own gig.", status_code=403)


def submit_payment(
    *,
    app_config,
    user: User,
    mpesa_code: str,
    purpose: PaymentPurpose,
    gig: Gig | None = None,
) -> Payment:
    """Create a PENDING payment row for manual admin verification.

    Raises PaymentError for validation failures, including the code-
    reuse race condition called out in PRD §12 finding #5: the
    UNIQUE constraint on mpesa_code is the real guard, and we catch
    the resulting IntegrityError instead of letting it surface as a
    raw 500.
    """
    if not validate_mpesa_code(mpesa_code):
        raise PaymentError(
            "That doesn't look like a valid M-Pesa confirmation code."
        )
    code = normalize_mpesa_code(mpesa_code)
    _validate_boost_target(user, purpose, gig)

    amount = fee_for_purpose(app_config, purpose)

    payment = Payment(
        user_id=user.id,
        gig_id=gig.id if gig else None,
        mpesa_code=code,
        amount=amount,
        purpose=purpose,
        status=PaymentStatus.PENDING,
        method=PaymentMethod.MANUAL,
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


def initiate_stk_payment(
    *,
    app_config,
    user: User,
    purpose: PaymentPurpose,
    gig: Gig | None = None,
    phone_number: str | None = None,
) -> Payment:
    """Phase 5: kick off a Daraja STK Push and record a PENDING
    payment correlated by checkout_request_id. The actual VERIFIED
    transition happens in handle_daraja_callback when Safaricom's
    callback lands — this function only ever leaves the payment
    PENDING.
    """
    _validate_boost_target(user, purpose, gig)
    amount = fee_for_purpose(app_config, purpose)
    target_phone = (phone_number or user.phone_number or "").strip()
    if not target_phone:
        raise PaymentError("We don't have a phone number to send the STK prompt to.")

    reference = f"gig{gig.id}" if gig else f"user{user.id}"
    description = "Comradeplug boost" if purpose == PaymentPurpose.BOOST else "Comradeplug subscription"

    daraja_response = daraja_service.initiate_stk_push(
        app_config,
        phone_number=target_phone,
        amount=int(amount),
        account_reference=reference,
        description=description,
    )

    payment = Payment(
        user_id=user.id,
        gig_id=gig.id if gig else None,
        mpesa_code=None,
        amount=amount,
        purpose=purpose,
        status=PaymentStatus.PENDING,
        method=PaymentMethod.STK_PUSH,
        checkout_request_id=daraja_response.get("CheckoutRequestID"),
        merchant_request_id=daraja_response.get("MerchantRequestID"),
        phone_number=target_phone,
    )
    db.session.add(payment)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise PaymentError("That payment request is already in flight.", status_code=409)
    return payment


def handle_daraja_callback(callback_data: dict) -> Payment | None:
    """Applies the result of a parsed Daraja callback
    (daraja_service.parse_callback output) to the matching PENDING
    payment. Returns the updated Payment, or None if no matching
    payment was found (e.g. a stale/duplicate callback) — the route
    still returns 200 to Safaricom either way, since retrying a
    callback we can't match won't help.
    """
    payment = Payment.query.filter_by(
        checkout_request_id=callback_data["checkout_request_id"]
    ).first()
    if payment is None or payment.status != PaymentStatus.PENDING:
        return payment

    if not callback_data["success"]:
        payment.status = PaymentStatus.REJECTED
        db.session.add(payment)
        db.session.commit()
        return payment

    receipt = callback_data.get("mpesa_receipt")
    if not receipt or callback_data.get("amount") != float(payment.amount):
        current_app.logger.warning("Rejected Daraja callback with mismatched payment details.")
        return payment
    callback_phone = _normalise_phone(callback_data.get("phone_number"))
    expected_phone = _normalise_phone(payment.phone_number)
    if callback_phone and expected_phone and callback_phone != expected_phone:
        current_app.logger.warning("Rejected Daraja callback with mismatched phone number.")
        return payment

    payment.mpesa_code = normalize_mpesa_code(str(receipt))
    payment.status = PaymentStatus.VERIFIED
    db.session.add(payment)
    db.session.commit()

    apply_verified_payment(payment)
    return payment


def _normalise_phone(phone: str | None) -> str:
    """Compare Kenyan phone formats without accepting arbitrary values."""
    digits = "".join(char for char in (phone or "") if char.isdigit())
    if digits.startswith("0") and len(digits) == 10:
        return "254" + digits[1:]
    if digits.startswith("254") and len(digits) == 12:
        return digits
    return digits


def redeem_boost_credit(*, user: User, gig: Gig) -> Payment:
    """Phase 10: spend one referral-earned free boost credit instead
    of paying. Raises PaymentError if the user has none."""
    if user.free_boost_credits <= 0:
        raise PaymentError("You don't have a free boost credit to redeem.")
    if gig.poster_id != user.id:
        raise PaymentError("You can only boost your own gig.", status_code=403)

    user.free_boost_credits -= 1
    payment = Payment(
        user_id=user.id,
        gig_id=gig.id,
        mpesa_code=None,
        amount=0,
        purpose=PaymentPurpose.BOOST,
        status=PaymentStatus.VERIFIED,
        method=PaymentMethod.CREDIT,
    )
    db.session.add(user)
    db.session.add(payment)
    db.session.commit()

    apply_verified_payment(payment)
    return payment


def apply_verified_payment(payment: Payment) -> None:
    """Side effects of a payment becoming VERIFIED (manual admin
    approval, a Daraja callback, or a redeemed credit): activate the
    boost or extend the subscription. Idempotent-ish — re-running it
    just re-extends the window, which is an acceptable behavior (no
    destructive effect)."""
    now = datetime.now(timezone.utc)

    if payment.purpose == PaymentPurpose.BOOST and payment.gig is not None:
        payment.gig.is_boosted = True
        payment.gig.boost_expires_at = now + timedelta(hours=BOOST_DURATION_HOURS)
        db.session.add(payment.gig)

    elif payment.purpose == PaymentPurpose.SUBSCRIPTION:
        payment.user.is_verified_entrepreneur = True
        db.session.add(payment.user)

    db.session.commit()

    purpose_label = "boost" if payment.purpose == PaymentPurpose.BOOST else "entrepreneur subscription"
    whatsapp_service.notify_payment_verified(
        current_app.config,
        to_phone=payment.user.phone_number,
        purpose_label=purpose_label,
        logger=current_app.logger,
    )


def verify_payment(payment: Payment, approve: bool) -> Payment:
    payment.status = PaymentStatus.VERIFIED if approve else PaymentStatus.REJECTED
    db.session.add(payment)
    db.session.commit()

    if approve:
        apply_verified_payment(payment)

    return payment
