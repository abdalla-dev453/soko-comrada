import os

import pytest

os.environ.setdefault("FLASK_ENV", "testing")
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("JWT_SECRET_KEY", "test-jwt-secret")
os.environ.setdefault("ALLOWED_STUDENT_EMAIL_DOMAINS", "jkuat.ac.ke")

from app import create_app  # noqa: E402
from app.extensions import db as _db  # noqa: E402


@pytest.fixture()
def app():
    application = create_app("testing")
    with application.app_context():
        _db.create_all()
        yield application
        _db.session.remove()
        _db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def db(app):
    return _db


def register_user(client, **overrides):
    payload = {
        "name": "Amina Wanjiru",
        "email": "amina@jkuat.ac.ke",
        "password": "supersecret123",
        "phone_number": "+254712345678",
        "university": "JKUAT",
        "campus_location": "JKUAT Juja",
    }
    payload.update(overrides)
    return client.post("/api/auth/register", json=payload)


def auth_header(access_token: str) -> dict:
    return {"Authorization": f"Bearer {access_token}"}
