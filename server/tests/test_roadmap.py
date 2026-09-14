"""Tests for the post-MVP roadmap features:
  Phase 5  — Daraja STK Push plumbing (unit, no real Safaricom call)
  Phase 6  — admin dispute resolution
  Phase 9  — admin un-flagging a gig
  Phase 10 — referral code, credit award, credit redemption
"""

from unittest.mock import MagicMock, patch

from tests.conftest import auth_header, register_user


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def _register_and_get(client, email="user@jkuat.ac.ke", **kwargs):
    resp = register_user(client, email=email, **kwargs)
    return resp.get_json()


def _create_gig(client, token, **overrides):
    payload = {
        "title": "Quick task",
        "description": "A simple 10-minute errand around campus.",
        "budget": "200",
        "gig_type": "TASK_NEEDED",
        "category": "errands",
        "campus_location": "JKUAT Juja",
    }
    payload.update(overrides)
    return client.post("/api/gigs", json=payload, headers=auth_header(token))


def _apply_accept_complete_first_side(client, poster, hustler, gig_id):
    """Helper: apply → accept → first-side complete, return app_id."""
    app_id = client.post(
        f"/api/gigs/{gig_id}/applications", json={},
        headers=auth_header(hustler["access_token"]),
    ).get_json()["application"]["id"]
    client.patch(
        f"/api/applications/{app_id}",
        json={"status": "ACCEPTED"},
        headers=auth_header(poster["access_token"]),
    )
    client.post(f"/api/gigs/{gig_id}/complete", headers=auth_header(poster["access_token"]))
    return app_id


# --------------------------------------------------------------------------- #
# Phase 5 — Daraja STK Push unit tests (no real Safaricom call)
# --------------------------------------------------------------------------- #

def test_stk_push_without_credentials_returns_503(client):
    """Without DARAJA_* env vars, the route returns a clear 503 rather
    than crashing — the frontend can degrade to the manual /verify path."""
    user = _register_and_get(client)
    resp = client.post(
        "/api/payments/stk-push",
        json={"purpose": "SUBSCRIPTION"},
        headers=auth_header(user["access_token"]),
    )
    assert resp.status_code in (400, 503)   # DarajaError raises 503


def test_daraja_callback_bad_payload_returns_400(client):
    """Garbage sent to the public callback endpoint should be rejected
    cleanly, not raise a 500."""
    resp = client.post(
        "/api/payments/daraja/callback",
        json={"garbage": "data"},
    )
    assert resp.status_code == 400


def test_daraja_callback_unknown_checkout_id_still_200(client):
    """A valid-looking callback for a payment we don't know about must
    still return 200 — or Safaricom will retry indefinitely."""
    payload = {
        "Body": {
            "stkCallback": {
                "MerchantRequestID": "abc123",
                "CheckoutRequestID": "ws_CO_999999",
                "ResultCode": 0,
                "ResultDesc": "Success",
                "CallbackMetadata": {
                    "Item": [
                        {"Name": "Amount", "Value": 50},
                        {"Name": "MpesaReceiptNumber", "Value": "QAB1CDE2FG"},
                        {"Name": "PhoneNumber", "Value": 254712345678},
                    ]
                },
            }
        }
    }
    resp = client.post("/api/payments/daraja/callback", json=payload)
    assert resp.status_code == 200


# --------------------------------------------------------------------------- #
# Phase 5 — STK Push mock: happy path with a patched Daraja call
# --------------------------------------------------------------------------- #

def test_stk_push_creates_pending_payment_when_daraja_responds(client, app):
    with app.app_context():
        app.config["DARAJA_CONSUMER_KEY"] = "fake-key"
        app.config["DARAJA_CONSUMER_SECRET"] = "fake-secret"
        app.config["DARAJA_SHORTCODE"] = "174379"
        app.config["DARAJA_PASSKEY"] = "fake-passkey"
        app.config["DARAJA_CALLBACK_URL"] = "https://example.com/callback"

    user = _register_and_get(client)

    mock_response = {
        "ResponseCode": "0",
        "ResponseDescription": "Success",
        "MerchantRequestID": "mr-001",
        "CheckoutRequestID": "ws_CO_001",
        "CustomerMessage": "STK sent",
    }

    with patch("app.services.daraja_service.requests.get") as mock_get, \
         patch("app.services.daraja_service.requests.post") as mock_post:

        mock_get.return_value = MagicMock(
            ok=True, json=lambda: {"access_token": "fake-token"}
        )
        mock_get.return_value.raise_for_status = lambda: None

        mock_post.return_value = MagicMock(ok=True, json=lambda: mock_response)
        mock_post.return_value.raise_for_status = lambda: None

        resp = client.post(
            "/api/payments/stk-push",
            json={"purpose": "SUBSCRIPTION"},
            headers=auth_header(user["access_token"]),
        )

    assert resp.status_code == 202
    body = resp.get_json()["payment"]
    assert body["status"] == "PENDING"
    assert body["method"] == "STK_PUSH"


# --------------------------------------------------------------------------- #
# Phase 6 — admin resolves a dispute
# --------------------------------------------------------------------------- #

def test_admin_can_resolve_dispute(client, db, app):
    from app.models.user import User

    poster = _register_and_get(client, email="poster2@jkuat.ac.ke", name="Poster Two")
    hustler = _register_and_get(client, email="hustler2@jkuat.ac.ke", name="Hustler Two")
    gig_id = _create_gig(client, poster["access_token"]).get_json()["gig"]["id"]

    _apply_accept_complete_first_side(client, poster, hustler, gig_id)

    # Hustler disputes
    client.post(
        f"/api/gigs/{gig_id}/dispute",
        json={"reason": "Job was never done."},
        headers=auth_header(hustler["access_token"]),
    )

    # Make poster an admin
    with app.app_context():
        user = User.query.filter_by(email="poster2@jkuat.ac.ke").first()
        user.is_admin = True
        db.session.commit()

    admin_token = client.post(
        "/api/auth/login",
        json={"email": "poster2@jkuat.ac.ke", "password": "supersecret123"},
    ).get_json()["access_token"]

    resolve_resp = client.post(
        f"/api/admin/disputes/{gig_id}/resolve",
        json={"resolution": "CANCELLED"},
        headers=auth_header(admin_token),
    )
    assert resolve_resp.status_code == 200
    assert resolve_resp.get_json()["gig"]["status"] == "CANCELLED"


# --------------------------------------------------------------------------- #
# Phase 9 — admin clears a moderation flag
# --------------------------------------------------------------------------- #

def test_admin_can_clear_moderation_flag(client, db, app):
    from app.models.user import User

    poster = _register_and_get(client, email="poster3@jkuat.ac.ke", name="Poster Three")
    flagged_resp = _create_gig(
        client, poster["access_token"],
        title="Do my assignment for me",
        description="Need someone to write and submit it.",
    )
    gig_id = flagged_resp.get_json()["gig"]["id"]

    # Confirm it's absent from the public feed
    feed_before = client.get("/api/gigs?campus=JKUAT Juja")
    ids_before = [g["id"] for g in feed_before.get_json()["gigs"]]
    assert gig_id not in ids_before

    # Find the auto-generated report
    with app.app_context():
        from app.models.report import Report
        report = Report.query.filter_by(reported_gig_id=gig_id, auto_generated=True).first()
        report_id = report.id
        user = User.query.filter_by(email="poster3@jkuat.ac.ke").first()
        user.is_admin = True
        db.session.commit()

    admin_token = client.post(
        "/api/auth/login",
        json={"email": "poster3@jkuat.ac.ke", "password": "supersecret123"},
    ).get_json()["access_token"]

    # Admin reviews and clears the flag (DISMISSED = false positive, gig goes live)
    clear_resp = client.patch(
        f"/api/admin/reports/{report_id}",
        json={"status": "DISMISSED"},
        headers=auth_header(admin_token),
    )
    assert clear_resp.status_code == 200

    # Gig now appears in the public feed (flag cleared)
    feed_after = client.get("/api/gigs?campus=JKUAT Juja")
    ids_after = [g["id"] for g in feed_after.get_json()["gigs"]]
    assert gig_id in ids_after


# --------------------------------------------------------------------------- #
# Phase 10 — referral growth loop
# --------------------------------------------------------------------------- #

def test_referral_code_is_generated_on_registration(client):
    user = _register_and_get(client)
    me = client.get("/api/auth/me", headers=auth_header(user["access_token"])).get_json()["user"]
    assert "referral_code" in me
    assert len(me["referral_code"]) == 7


def test_valid_referral_code_is_linked(client, db, app):
    from app.models.user import User

    referrer = _register_and_get(client, email="referrer@jkuat.ac.ke", name="Referrer")
    me = client.get("/api/auth/me", headers=auth_header(referrer["access_token"])).get_json()["user"]
    code = me["referral_code"]

    new_user_resp = register_user(
        client,
        email="newbie@jkuat.ac.ke",
        name="New Person",
        referral_code=code,
    )
    assert new_user_resp.status_code == 201

    with app.app_context():
        new_user = User.query.filter_by(email="newbie@jkuat.ac.ke").first()
        assert new_user.referred_by_id == referrer["user"]["id"]


def test_every_third_referral_awards_a_boost_credit(client, db, app):
    from app.models.user import User

    referrer = _register_and_get(client, email="refc@jkuat.ac.ke", name="Ref C")
    me = client.get("/api/auth/me", headers=auth_header(referrer["access_token"])).get_json()["user"]
    code = me["referral_code"]

    # Register 3 new users with the referral code
    for i in range(3):
        register_user(client, email=f"invitee{i}@jkuat.ac.ke", name=f"Invitee {i}", referral_code=code)

    with app.app_context():
        ref = User.query.filter_by(email="refc@jkuat.ac.ke").first()
        assert ref.free_boost_credits == 1


def test_redeem_credit_boosts_gig_without_mpesa(client, db, app):
    from app.models.user import User

    referrer = _register_and_get(client, email="refd@jkuat.ac.ke", name="Ref D")
    me = client.get("/api/auth/me", headers=auth_header(referrer["access_token"])).get_json()["user"]
    code = me["referral_code"]

    for i in range(3):
        register_user(client, email=f"inv2_{i}@jkuat.ac.ke", name=f"Inv2 {i}", referral_code=code)

    with app.app_context():
        ref = User.query.filter_by(email="refd@jkuat.ac.ke").first()
        assert ref.free_boost_credits == 1

    gig_id = _create_gig(client, referrer["access_token"]).get_json()["gig"]["id"]

    redeem_resp = client.post(
        "/api/payments/redeem-credit",
        json={"gig_id": gig_id},
        headers=auth_header(referrer["access_token"]),
    )
    assert redeem_resp.status_code == 200
    body = redeem_resp.get_json()
    assert body["payment"]["method"] == "CREDIT"
    assert body["payment"]["status"] == "VERIFIED"
    assert body["remaining_credits"] == 0

    # Gig should now be boosted
    gig = client.get(f"/api/gigs/{gig_id}").get_json()["gig"]
    assert gig["is_boosted"] is True
