
from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.extensions import db
from app.models.user import User


def get_current_user() -> User | None:
    user_id = get_jwt_identity()
    if user_id is None:
        return None
    return db.session.get(User, int(user_id))


def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        # Check the current database role rather than trusting a role claim
        # embedded in an older token. This makes demotions effective immediately.
        user = get_current_user()
        if user is None or not user.is_admin:
            return jsonify({
                "error": "forbidden", "message": "Admin access required."
            }), 403
        return fn(*args, **kwargs)
    return wrapper


def load_current_user(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if user is None:
            return jsonify({
                "error": "unauthorized", 'message': "Account not found."
            }), 401
        kwargs["current_user"] = user
        return fn(*args, **kwargs)
    return wrapper
