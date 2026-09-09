from tests.conftest import auth_header, register_user


def test_register_rejects_non_student_domain(client):
    resp = register_user(client, email="amina@gmail.com")
    assert resp.status_code == 422
    assert "email" in resp.get_json()["message"]


def test_register_and_login_flow(client):
    resp = register_user(client)
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["user"]["email"] == "amina@jkuat.ac.ke"
    assert "access_token" in body
    assert "refresh_token" in body

    login_resp = client.post(
        "/api/auth/login",
        json={"email": "amina@jkuat.ac.ke", "password": "supersecret123"},
    )
    assert login_resp.status_code == 200
    assert "access_token" in login_resp.get_json()


def test_login_rejects_wrong_password(client):
    register_user(client)
    resp = client.post(
        "/api/auth/login",
        json={"email": "amina@jkuat.ac.ke", "password": "wrong-password"},
    )
    assert resp.status_code == 401


def test_duplicate_registration_conflicts(client):
    register_user(client)
    resp = register_user(client)
    assert resp.status_code == 409


def test_me_requires_auth(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401


def test_me_returns_profile_when_authenticated(client):
    register_resp = register_user(client)
    token = register_resp.get_json()["access_token"]

    resp = client.get("/api/auth/me", headers=auth_header(token))
    assert resp.status_code == 200
    assert resp.get_json()["user"]["email"] == "amina@jkuat.ac.ke"


def test_refresh_issues_new_access_token(client):
    register_resp = register_user(client)
    refresh_token = register_resp.get_json()["refresh_token"]

    resp = client.post("/api/auth/refresh", headers=auth_header(refresh_token))
    assert resp.status_code == 200
    assert "access_token" in resp.get_json()
