from tests.conftest import auth_header, register_user


def test_submit_payment_requires_valid_mpesa_code_format(client):
    user = register_user(client).get_json()
    resp = client.post(
        "/api/payments/verify",
        json={"mpesa_code": "notacode", "purpose": "SUBSCRIPTION"},
        headers=auth_header(user["access_token"]),
    )
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "payment_error"


def test_submit_payment_success_creates_pending_record(client):
    user = register_user(client).get_json()
    resp = client.post(
        "/api/payments/verify",
        json={"mpesa_code": "QAB1CDE2FG", "purpose": "SUBSCRIPTION"},
        headers=auth_header(user["access_token"]),
    )
    assert resp.status_code == 201
    body = resp.get_json()["payment"]
    assert body["status"] == "PENDING"
    assert body["purpose"] == "SUBSCRIPTION"


def test_duplicate_mpesa_code_is_rejected(client):
    user = register_user(client).get_json()
    first = client.post(
        "/api/payments/verify",
        json={"mpesa_code": "QAB1CDE2FG", "purpose": "SUBSCRIPTION"},
        headers=auth_header(user["access_token"]),
    )
    assert first.status_code == 201

    second = client.post(
        "/api/payments/verify",
        json={"mpesa_code": "QAB1CDE2FG", "purpose": "SUBSCRIPTION"},
        headers=auth_header(user["access_token"]),
    )
    assert second.status_code == 409


def test_non_admin_cannot_see_pending_payments(client):
    user = register_user(client).get_json()
    resp = client.get("/api/admin/payments/pending", headers=auth_header(user["access_token"]))
    assert resp.status_code == 403


def test_admin_can_approve_payment_and_it_activates_subscription(client, db, app):
    from app.models.user import User

    user_data = register_user(client).get_json()

    with app.app_context():
        user = User.query.filter_by(email="amina@jkuat.ac.ke").first()
        user.is_admin = True
        db.session.commit()

    admin_login = client.post(
        "/api/auth/login", json={"email": "amina@jkuat.ac.ke", "password": "supersecret123"}
    ).get_json()

    submit_resp = client.post(
        "/api/payments/verify",
        json={"mpesa_code": "QAB1CDE2FG", "purpose": "SUBSCRIPTION"},
        headers=auth_header(admin_login["access_token"]),
    )
    payment_id = submit_resp.get_json()["payment"]["id"]

    decision_resp = client.post(
        f"/api/admin/payments/{payment_id}/decision",
        json={"approve": True},
        headers=auth_header(admin_login["access_token"]),
    )
    assert decision_resp.status_code == 200
    assert decision_resp.get_json()["payment"]["status"] == "VERIFIED"

    profile = client.get("/api/auth/me", headers=auth_header(admin_login["access_token"]))
    assert profile.get_json()["user"]["is_verified_entrepreneur"] is True
