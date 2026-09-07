
import os

from flask import Flask, jsonify

from app.config import get_config
from app.extensions import cors, db, jwt, limiter, migrate


def create_app(env_name: str | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(get_config(env_name))

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # --- Extensions ---
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}},
        supports_credentials=True,
    )
    limiter.init_app(app)

    # Import models so they're registered on the SQLAlchemy metadata
    # before migrations or `db.create_all()` run.
    # from app import models 

    # # --- Blueprints ---
    # from app.blueprints.auth.routes import auth_bp
    # from app.blueprints.gigs.routes import gigs_bp
    # from app.blueprints.applications.routes import applications_bp
    # from app.blueprints.payments.routes import payments_bp
    # from app.blueprints.reviews.routes import reviews_bp
    # from app.blueprints.admin.routes import admin_bp

    # app.register_blueprint(auth_bp, url_prefix="/api/auth")
    # app.register_blueprint(gigs_bp, url_prefix="/api/gigs")
    # app.register_blueprint(applications_bp, url_prefix="/api/applications")
    # app.register_blueprint(payments_bp, url_prefix="/api/payments")
    # app.register_blueprint(reviews_bp, url_prefix="/api/reviews")
    # app.register_blueprint(admin_bp, url_prefix="/api/admin")

    # register_error_handlers(app)

    @app.get("/api/health")
    def health_check():
        return jsonify({"status": "ok", "service": "soko-comrada-api"}), 200

    return app


def register_error_handlers(app: Flask) -> None:
    """Unified JSON error responses so the frontend never has to guess
    the shape of an error payload."""

    @app.errorhandler(400)
    def bad_request(err):
        return jsonify({"error": "bad_request", "message": str(err.description)}), 400

    @app.errorhandler(401)
    def unauthorized(err):
        return jsonify({"error": "unauthorized", "message": str(err.description)}), 401

    @app.errorhandler(403)
    def forbidden(err):
        return jsonify({"error": "forbidden", "message": str(err.description)}), 403

    @app.errorhandler(404)
    def not_found(err):
        return jsonify({"error": "not_found", "message": str(err.description)}), 404

    @app.errorhandler(409)
    def conflict(err):
        return jsonify({"error": "conflict", "message": str(err.description)}), 409

    @app.errorhandler(422)
    def unprocessable(err):
        message = getattr(err, "data", None) or str(err.description)
        return jsonify({"error": "validation_error", "message": message}), 422

    @app.errorhandler(429)
    def rate_limited(err):
        return (
            jsonify(
                {
                    "error": "rate_limited",
                    "message": "Too many requests. Please slow down and try again shortly.",
                }
            ),
            429,
        )

    @app.errorhandler(500)
    def server_error(err):
        app.logger.exception("Unhandled server error")
        return (
            jsonify({"error": "server_error", "message": "Something went wrong."}),
            500,
        )
