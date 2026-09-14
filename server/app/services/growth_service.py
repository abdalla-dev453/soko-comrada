"""Referral growth loop (Phase 10 roadmap item).

Deliberately simple: every 3rd successful referral earns the
referrer one free boost credit, redeemable instead of an M-Pesa
payment when boosting a gig (see payment_service.redeem_boost_credit).
"""

from app.extensions import db
from app.models.user import User

REFERRALS_PER_CREDIT = 3


def find_referrer(referral_code: str | None) -> User | None:
    if not referral_code:
        return None
    return User.query.filter_by(referral_code=referral_code.strip().upper()).first()


def link_referral(new_user: User, referrer: User | None) -> None:
    """Call once, right after a new user is created. Links the
    referral and awards a credit if this referral completes a batch
    of REFERRALS_PER_CREDIT."""
    if referrer is None or referrer.id == new_user.id:
        return

    new_user.referred_by_id = referrer.id
    db.session.add(new_user)
    db.session.flush()  # ensure the count below sees this referral

    referred_count = User.query.filter_by(referred_by_id=referrer.id).count()
    if referred_count % REFERRALS_PER_CREDIT == 0:
        referrer.free_boost_credits += 1
        db.session.add(referrer)

