import os
import secrets
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


def _positive_int(name: str, default: int) -> int:
    """Read a positive integer setting without accepting unsafe values."""
    try:
        value = int(os.environ.get(name, str(default)))
    except ValueError as exc:
        raise RuntimeError(f"{name} must be an integer.") from exc
    if value <= 0:
        raise RuntimeError(f"{name} must be greater than zero.")
    return value


class BaseConfig:
    """Shared configuration across all environments."""

    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_urlsafe(48)

    SQLALCHEMY_DATABASE_URI = _build_db_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
    }

    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or secrets.token_urlsafe(48)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        minutes=_positive_int("JWT_ACCESS_TOKEN_EXPIRES_MINUTES", 30)
    )
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(
        days=_positive_int("JWT_REFRESH_TOKEN_EXPIRES_DAYS", 30)
    )
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_HEADER_TYPE = "Bearer"

    CORS_ORIGINS = _split_csv(os.environ.get("CORS_ORIGINS", "http://localhost:5173"))

    RATELIMIT_STORAGE_URI = os.environ.get("RATELIMIT_STORAGE_URI", "memory://")
    RATELIMIT_DEFAULT = "200 per hour"
    RATELIMIT_HEADERS_ENABLED = True

    ALLOWED_STUDENT_EMAIL_DOMAINS = _split_csv(
        os.environ.get("ALLOWED_STUDENT_EMAIL_DOMAINS", "jkuat.ac.ke,ku.ac.ke,uonbi.ac.ke,mut.ac.ke,karu.ac.ke,kyu.ac.ke,egerton.ac.ke,moi.ac.ke,maseno.ac.ke,dkut.ac.ke,tukenya.ac.ke")
    )

    

    MPESA_TILL_NUMBER = os.environ.get("MPESA_TILL_NUMBER", "000000")
    BOOST_FEE_KES = float(os.environ.get("BOOST_FEE_KES", "50"))
    SUBSCRIPTION_FEE_KES = float(os.environ.get("SUBSCRIPTION_FEE_KES", "200"))

    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "/tmp/soko-comrada-uploads")
    MAX_CONTENT_LENGTH = _positive_int("MAX_CONTENT_LENGTH_MB", 5) * 1024 * 1024

    GIGS_PER_PAGE = 15


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_ECHO = False


class TestingConfig(BaseConfig):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "TEST_DATABASE_URL", "sqlite:///:memory:"
    )
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)
    RATELIMIT_ENABLED = False


class ProductionConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_ECHO = False


def validate_production_config(app_config: dict) -> None:
    """Fail closed when a production deployment uses placeholder secrets."""
    insecure_values = {"", "dev-secret-key-change-me", "dev-jwt-secret-change-me", "change-me"}
    for key in ("SECRET_KEY", "JWT_SECRET_KEY"):
        if not os.environ.get(key):
            raise RuntimeError(f"{key} must be explicitly configured in production.")
        value = app_config.get(key)
        if not isinstance(value, str) or len(value) < 32 or value in insecure_values:
            raise RuntimeError(
                f"{key} must be a unique, random value of at least 32 characters in production."
            )

    origins = app_config.get("CORS_ORIGINS", [])
    if not origins or "*" in origins:
        raise RuntimeError("CORS_ORIGINS must be an explicit, non-wildcard allowlist in production.")

    if app_config.get("RATELIMIT_STORAGE_URI", "memory://").startswith("memory://"):
        raise RuntimeError(
            "RATELIMIT_STORAGE_URI must use a shared backend (for example Redis) in production."
        )


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config(env_name: str | None = None):
    env_name = env_name or os.environ.get("FLASK_ENV", "development")
    return config_by_name.get(env_name, DevelopmentConfig)
