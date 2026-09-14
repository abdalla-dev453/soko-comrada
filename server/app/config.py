"""
Environment-based configuration classes for Soko Comrada.

Loaded via the application factory in app/__init__.py, selected by the
FLASK_ENV / APP_ENV environment variable. All secrets and connection
details are pulled from environment variables (see .env.example) —
nothing sensitive is hardcoded here, per PRD §12 (finding #4:
hardcoded DB credentials must not ship).
"""

import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()


def _build_db_uri() -> str:
    """Build the SQLAlchemy database URI from discrete env vars,
    unless a full DATABASE_URL override is provided."""
    override = os.environ.get("DATABASE_URL")
    if override:
        return override

    user = os.environ.get("DB_USER", "soko_app")
    password = os.environ.get("DB_PASSWORD", "")
    host = os.environ.get("DB_HOST", "localhost")
    port = os.environ.get("DB_PORT", "3306")
    name = os.environ.get("DB_NAME", "soko_comrada")
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}?charset=utf8mb4"


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


class BaseConfig:
    """Shared configuration across all environments."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

    SQLALCHEMY_DATABASE_URI = _build_db_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
        "pool_size": int(os.environ.get("DB_POOL_SIZE", "5")),
        "max_overflow": int(os.environ.get("DB_MAX_OVERFLOW", "10")),
        "pool_timeout": int(os.environ.get("DB_POOL_TIMEOUT_SECONDS", "30")),
    }

    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-jwt-secret-change-me")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        minutes=int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES_MINUTES", "30"))
    )
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(
        days=int(os.environ.get("JWT_REFRESH_TOKEN_EXPIRES_DAYS", "30"))
    )
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_HEADER_TYPE = "Bearer"

    CORS_ORIGINS = _split_csv(os.environ.get("CORS_ORIGINS", "http://localhost:5173"))

    RATELIMIT_STORAGE_URI = os.environ.get("RATELIMIT_STORAGE_URI", "memory://")
    # Production must use a shared backend so a second worker cannot bypass
    # limits maintained in process memory.
    RATELIMIT_DEFAULT = "200 per hour"

    ALLOWED_STUDENT_EMAIL_DOMAINS = _split_csv(
        os.environ.get("ALLOWED_STUDENT_EMAIL_DOMAINS", "jkuat.ac.ke,ku.ac.ke,uonbi.ac.ke")
    )

    MPESA_TILL_NUMBER = os.environ.get("MPESA_TILL_NUMBER", "000000")
    BOOST_FEE_KES = float(os.environ.get("BOOST_FEE_KES", "50"))
    SUBSCRIPTION_FEE_KES = float(os.environ.get("SUBSCRIPTION_FEE_KES", "200"))

    SMTP_HOST = os.environ.get("SMTP_HOST", "")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
    SMTP_USERNAME = os.environ.get("SMTP_USERNAME", "")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
    SMTP_FROM_ADDRESS = os.environ.get("SMTP_FROM_ADDRESS", "notifications@sokocomrada.app")
    SMTP_USE_TLS = os.environ.get("SMTP_USE_TLS", "true").lower() == "true"

    # --- Phase 5: Daraja STK Push ---
    DARAJA_ENV = os.environ.get("DARAJA_ENV", "sandbox")
    DARAJA_CONSUMER_KEY = os.environ.get("DARAJA_CONSUMER_KEY", "")
    DARAJA_CONSUMER_SECRET = os.environ.get("DARAJA_CONSUMER_SECRET", "")
    DARAJA_SHORTCODE = os.environ.get("DARAJA_SHORTCODE", "")
    DARAJA_PASSKEY = os.environ.get("DARAJA_PASSKEY", "")
    DARAJA_CALLBACK_URL = os.environ.get("DARAJA_CALLBACK_URL", "")
    DARAJA_CALLBACK_SECRET = os.environ.get("DARAJA_CALLBACK_SECRET", "")

    # --- Phase 7: WhatsApp Business Cloud API ---
    WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN", "")
    WHATSAPP_PHONE_NUMBER_ID = os.environ.get("WHATSAPP_PHONE_NUMBER_ID", "")

    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "/tmp/soko-comrada-uploads")
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH_MB", "5")) * 1024 * 1024

    GIGS_PER_PAGE = 15
    JSON_SORT_KEYS = False


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_ECHO = False


class TestingConfig(BaseConfig):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "TEST_DATABASE_URL", "sqlite:///:memory:"
    )
    # SQLite's in-memory StaticPool does not accept QueuePool options.
    SQLALCHEMY_ENGINE_OPTIONS = {}
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)
    RATELIMIT_ENABLED = False


class ProductionConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_ECHO = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    @classmethod
    def validate(cls) -> None:
        insecure = {"dev-secret-key-change-me", "dev-jwt-secret-change-me", "change-me"}
        missing = [key for key in ("SECRET_KEY", "JWT_SECRET_KEY") if not os.environ.get(key) or os.environ.get(key) in insecure]
        if missing:
            raise RuntimeError("Production requires strong values for: " + ", ".join(missing))
        if cls.RATELIMIT_STORAGE_URI == "memory://":
            raise RuntimeError("Production requires a shared RATELIMIT_STORAGE_URI (for example Redis).")
        if cls.DARAJA_CALLBACK_URL and not cls.DARAJA_CALLBACK_SECRET:
            raise RuntimeError("DARAJA_CALLBACK_SECRET is required when Daraja callbacks are enabled.")


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config(env_name: str | None = None):
    env_name = env_name or os.environ.get("FLASK_ENV", "development")
    config = config_by_name.get(env_name, DevelopmentConfig)
    if config is ProductionConfig:
        config.validate()
    return config
