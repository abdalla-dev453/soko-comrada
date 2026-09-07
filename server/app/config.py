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
    RATELIMIT_DEFAULT = "200 per hour"

    ALLOWED_STUDENT_EMAIL_DOMAINS = _split_csv(
        os.environ.get("ALLOWED_STUDENT_EMAIL_DOMAINS", "jkuat.ac.ke,ku.ac.ke,uonbi.ac.ke")
    )

    MPESA_TILL_NUMBER = os.environ.get("MPESA_TILL_NUMBER", "000000")
    BOOST_FEE_KES = float(os.environ.get("BOOST_FEE_KES", "50"))
    SUBSCRIPTION_FEE_KES = float(os.environ.get("SUBSCRIPTION_FEE_KES", "200"))

    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "/tmp/soko-comrada-uploads")
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH_MB", "5")) * 1024 * 1024

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


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config(env_name: str | None = None):
    env_name = env_name or os.environ.get("FLASK_ENV", "development")
    return config_by_name.get(env_name, DevelopmentConfig)
